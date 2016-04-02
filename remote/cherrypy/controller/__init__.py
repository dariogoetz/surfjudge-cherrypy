import cherrypy
import json
from ..lib.access_conditions import *

from keys import *


class CherrypyWebInterface(object):
    N_BEST_WAVES = 2
    DEFAULT_NUMBER_OF_WAVES = 10
    DEFAULT_DURATION = 15


    T_FORMAT = '%H:%M'
    D_FORMAT = '%d.%m.%Y'
    DT_FORMAT = '%Y-%m-%dT%H:%M'
    DTS_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, mount_location = '/'):
        self.mount_location = mount_location
        return


    def _standard_env(self):
        env = {}
        env['mount_loc'] = self.mount_location
        username = cherrypy.session.get(KEY_USERNAME)
        env['global_username'] = username

        ui = cherrypy.session.get(KEY_USER_INFO)
        if ui is None:
            ui = cherrypy.engine.publish(KEY_ENGINE_USER_INFO, username).pop()
        if ui is None:
            ui = {}

        roles = ui.get(KEY_ROLES, [])
        env['global_is_admin'] = KEY_ROLE_ADMIN in roles
        env['global_is_commentator'] = KEY_ROLE_COMMENTATOR in roles
        env['global_is_judge'] = KEY_ROLE_JUDGE in roles
        env['global_is_headjudge'] = KEY_ROLE_HEADJUDGE in roles
        env['global_logged_in'] = bool(username)
        return env


    def render_html(self, context = None, template = None):
        if context is None:
            context = {}
        env = self._standard_env()
        env.update(context)

        if template:
            tpl = cherrypy.engine.publish(KEY_ENGINE_LOOKUP_TEMPLATE, template).pop()
        else:
            tpl = None

        # Render the template into the response body
        if tpl:
            return tpl.render(**env)
        else:
            return env


    def collect_heat_info(self, heat_id, force_from_db=False):
        query_info = {'heat_id': heat_id}

        # if heat_id is None, only currently active heat infos are provided
        if heat_id is None:
            return cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop()

        # if a heat_id is provided, first try state manager for speed
        if not force_from_db:
            heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop()
            if heat_info is not None and len(heat_info) > 0:
                return heat_info

        # if not active, get heat_info from database
        heat_info = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEAT_INFO, query_info).pop()
        if len(heat_info) > 0:
            heat_info = heat_info[0]
        else:
            print 'do_activate_heat: Error: heat_id not in DB'
            return None

        if heat_info.get('number_of_waves') is None:
            heat_info['number_of_waves'] = self.DEFAULT_NUMBER_OF_WAVES

        heat_info[KEY_HEAT_ID] = heat_id
        judges = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGES_FOR_HEAT, heat_id).pop()
        for judge in judges:
            if judge[KEY_HEAT_ID] != heat_id:
                continue
            judge_id = judge[KEY_JUDGE_ID]
            first_name = judge['first_name']
            last_name = judge['last_name']
            username = judge['username']
            heat_info.setdefault('judges', {})[judge_id] = {KEY_HEAT_ID: heat_id,
                                                            KEY_JUDGE_ID: judge_id,
                                                            'judge_first_name': first_name,
                                                            'judge_last_name': last_name,
                                                            'judge_username': username}
        surfer_data = self.collect_participants(heat_id)
        heat_info['participants'] = surfer_data
        return heat_info


    def collect_participants(self, heat_id, fill_proposal=False, confirmed_participants=None):
        if confirmed_participants is None:
            participants = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_PARTICIPANTS, heat_id).pop()
        else:
            participants = confirmed_participants

        # set 'proposal' to False
        for p in participants:
            p.setdefault('proposal', False)

        if fill_proposal:
            existing_surfer_ids = set([p['surfer_id'] for p in participants])
            proposed_participants = cherrypy.engine.publish(KEY_ENGINE_TM_GET_ADVANCING_SURFERS, heat_id).pop()

            db_seeds = [int(p.get('seed')) for p in participants if p.get('seed') is not None]
            fill_in_participant_seeds = set(proposed_participants.keys()) - set(db_seeds)
            if len(fill_in_participant_seeds) > 0:
                for seed in fill_in_participant_seeds:
                    from_heat = proposed_participants.get(seed, {}).get('from_heat_id')
                    from_place = proposed_participants.get(seed, {}).get('from_place')
                    print u'collecting participants: advancing surfer from Heat {}, {}. place'.format(from_heat, from_place)
                    # get surfer_id from results table
                    heat_result = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_RESULTS, {'heat_id': from_heat, 'place': from_place}).pop()
                    if len(heat_result) > 0:
                        heat_result = heat_result[0]
                    if 'surfer_id' not in heat_result:
                        print u'collecting participants: no placing (yet) for Heat {}, {}. place (starting from 1)'.format(from_heat, from_place+1)
                        continue
                    surfer_id = heat_result.get('surfer_id')
                    if surfer_id in existing_surfer_ids:
                        # advancing surfer already exists on other seed -> do not include
                        continue
                    surfer_info = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_SURFERS, {'id': surfer_id}).pop()
                    new_participant = {}
                    new_participant.update(surfer_info[0])
                    new_participant['proposal'] = True
                    new_participant['surfer_id'] = surfer_id
                    new_participant['heat_id'] = heat_id
                    new_participant['seed'] = seed
                    participants.append(new_participant)

        participants = self._complete_participants(participants)
        return sorted(participants, key=lambda x: x['seed'])

    def _get_scores(self, heat_id, judges):
        heat_id = int(heat_id)
        query_info = {KEY_HEAT_ID: heat_id}
        scores = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_SCORES, query_info).pop()
        scores_by_surfer_wave = {}
        for score in scores:
            # filter only scores from named judges
            if score[KEY_JUDGE_ID] not in judges:
                continue
            scores_by_surfer_wave.setdefault(score['surfer_id'], {}).setdefault(score['wave'], {})[score[KEY_JUDGE_ID]] = score
        return scores_by_surfer_wave


    def _get_id2color(self, participants):
        return {p['surfer_id']: p['surfer_color'] for p in participants}

    def _get_id2name(self, participants):
        return {p['surfer_id']: p['name'] for p in participants}

    def _get_color2id(self, participants):
        return {p['surfer_color']: p['surfer_id'] for p in participants}


    def _complete_participants(self, participants):
        import utils

        confirmed_participants = [p for p in participants if not p.get('proposed')]
        proposed_participants = [p for p in participants if p.get('proposed')]

        colors = utils.read_lycra_colors('lycra_colors.csv')
        seed2color = {int(c['SEEDING']): c for c in colors.values()}

        # make participants complete
        # seed
        taken_seeds = set([p['seed'] for p in participants if 'seed' in p])
        all_seeds = set(range(max(taken_seeds)+2)) if len(taken_seeds)>0 else set([0])
        available_seeds = all_seeds - taken_seeds

        for p in confirmed_participants + proposed_participants:
            if 'seed' not in p:
                p['seed'] = sorted(available_seeds).pop(0)


        confirmed_participants = sorted(confirmed_participants, key=lambda x: x['seed'])
        proposed_participants = sorted(proposed_participants, key=lambda x: x['seed'])

        # color
        taken_colors = set([p['surfer_color'] for p in participants if 'surfer_color' in p])
        available_colors = [seed2color[s]['COLOR'] for s in sorted(seed2color) if seed2color[s]['COLOR'] not in taken_colors]

        for p in confirmed_participants + proposed_participants:
            if 'surfer_color' not in p:
                pref_c = seed2color[p['seed']]['COLOR']
                if pref_c not in taken_colors:
                    color = pref_c
                if pref_c in available_colors:
                    available_colors.remove(pref_c)
                else:
                    if len(available_colors) > 0:
                        color = available_colors.pop(0)
                    else:
                        print 'Warning: No more colors available'
                        color = list(taken_colors)[0]

                p['surfer_color'] = color
                taken_colors.add(pref_c)

        for participant in participants:
            participant['surfer_color_hex'] = colors.get(participant.get('surfer_color'), {}).get('HEX')
        return participants

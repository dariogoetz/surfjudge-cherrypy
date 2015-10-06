import cherrypy
import json
import os
from ..lib.access_conditions import *
from . import CherrypyWebInterface
import utils

from keys import *

class SurfJudgeWebInterface(CherrypyWebInterface):

    @cherrypy.expose
    #@require(is_admin())
    @cherrypy.tools.render(template = 'index.html')
    def index(self):
        context = self._standard_env()
        heats_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, None).pop()
        for heat_id, heat in heats_info.items():
            query_info = {KEY_HEAT_ID: int(heat_id)}
            # TODO: maybe store current scores in state object for faster access
            scores = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_SCORES, query_info).pop()
            heat['scores'] = json.loads(self.do_query_scores(heat_id=heat_id, get_for_all_judges=1))
        context['active_heats'] = heats_info
        return context


    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_JUDGE, KEY_ROLE_COMMENTATOR, KEY_ROLE_HEADJUDGE, KEY_ROLE_ADMIN))
    @cherrypy.tools.render(template='judge_hub.html')
    def judge_hub(self):
        data = self._standard_env()
        return data


    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_JUDGE)) # later ask for judge or similar
    @cherrypy.tools.render(template='judge_panel.html')
    def do_get_judge_panel(self, heat_id = None):
        if heat_id is None:
            return ''

        heat_id = int(heat_id)
        judge_id = cherrypy.session.get(KEY_JUDGE_ID)
        heats = cherrypy.engine.publish(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, judge_id).pop()
        data = self._standard_env()
        if len(heats) == 0:
            return ''

        if heat_id not in [h['heat_id'] for h in heats.values()]:
            print 'do_get_judge_panel: Is not judge for requested heat_id'
            return 'res'

        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)
        surfer_data = heat_info['participants']
        ids = map(str, surfer_data.get('surfer_id', []))
        colors = map(str, surfer_data.get('surfer_color', []))
        colors_hex = map(str, surfer_data.get('surfer_color_hex', []))
        data['judge_name'] = '{} {}'.format(heat_info['judges'][judge_id]['judge_first_name'], heat_info['judges'][judge_id]['judge_last_name'])
        data['surfers'] = dict(zip(ids, colors))
        data['surfer_color_names'] = colors
        data['surfer_color_colors'] = dict(zip(colors, colors_hex))
        data['number_of_waves'] = int(heat_info['number_of_waves'])
        return data

    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_COMMENTATOR)) # later ask for judge or similar
    @cherrypy.tools.render(template='commentator_hub.html')
    def commentator_hub(self):
        data = self._standard_env()
        return data

    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_COMMENTATOR)) # later ask for judge or similar
    @cherrypy.tools.render(template='commentator_panel.html')
    def do_get_commentator_panel(self, heat_id=None):
        if heat_id is None:
            return ''
        heat_id = int(heat_id)

        data = self._standard_env()

        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)
        surfer_data = heat_info['participants']
        ids = map(str, surfer_data.get('surfer_id', []))
        colors = map(str, surfer_data.get('surfer_color', []))
        colors_hex = map(str, surfer_data.get('surfer_color_hex', []))
        data['heat_id'] = heat_id
        data['surfers'] = dict(zip(ids, colors))
        data['surfer_color_names'] = colors
        data['surfer_color_colors'] = dict(zip(colors, colors_hex))
        data['number_of_waves'] = int(heat_info['number_of_waves'])
        return data


    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_JUDGE, KEY_ROLE_HEADJUDGE, KEY_ROLE_COMMENTATOR, KEY_ROLE_ADMIN))
    def do_query_scores(self, heat_id = None, judge_id = None, get_for_all_judges = None):
        roles = cherrypy.session.get(KEY_USER_INFO, {}).get(KEY_ROLES, [])

        if get_for_all_judges and (KEY_ROLE_HEADJUDGE in roles or KEY_ROLE_COMMENTATOR in roles or KEY_ROLE_ADMIN in roles):
            judge_id = None
        elif judge_id is None:
            judge_id = cherrypy.session.get(KEY_JUDGE_ID)
            if judge_id is None:
                print 'Error in "do_query_scores": No judge_id specified and is no judge'
                return '[]'
        else:
            if not KEY_ROLE_COMMENTATOR in roles and not KEY_ROLE_ADMIN in roles:
                print 'Error in "do_query_scores": judge_id specified but is no commentator'
                return '[]'

        if heat_id is None:
            if judge_id is None:
                print 'Error in "do_query_scores": No heat_id provided and no judge_id either (is probably commentator and requested for all judges)'
                return '[]'
            heats = cherrypy.engine.publish(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, judge_id).pop()
            if len(heats) == 0:
                print 'Error in "do_query_scores": No heat specified and no active heat available'
                return '[]'
            heat_id = heats.values()[0][KEY_HEAT_ID]

        heat_id = int(heat_id)
        query_info = {KEY_HEAT_ID: heat_id}

        if judge_id is not None:
            query_info[KEY_JUDGE_ID] = int(judge_id)

        scores = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_SCORES, query_info).pop()
        heat_info = self.collect_heat_info(heat_id)
        if heat_info is None:
            return '[]'

        participants = heat_info['participants']
        if 'surfer_id' not in participants or 'surfer_color' not in participants:
            print 'do_query_scores: no participants'
            return '[]'
        id2color = dict(zip(participants.get('surfer_id', []), participants.get('surfer_color', [])))
        out_scores = {}
        for score in scores:
            out_scores.setdefault(score['judge_id'], {}).setdefault(id2color[int(score['surfer_id'])], []).append( (score['wave'], score['score']) )

        for jid, s in out_scores.items():
            for color, vals in s.items():
                sorted_pairs = sorted(vals, key=lambda x: x[0])
                out_scores[jid][color] = [score for (wave, score) in sorted_pairs]

        if judge_id is not None:
            # not all judges scores were requested
            out_scores = out_scores.get(judge_id, {})
        else:
            # filter out only judges that are active for that heat
            judges = heat_info.get('judges', [])
            judges_with_scores = out_scores.keys()
            for jid in judges_with_scores:
                if jid not in judges:
                    del out_scores[jid]
                    print 'do_query_scores: filtered out scores for inactive judge {}'.format(jid)
        return json.dumps(out_scores)

    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_JUDGE, KEY_ROLE_ADMIN))
    def do_insert_score(self, score = None, heat_id = None, judge_id = None):
        if score is None:
            return
        #score = score.encode('utf-8')
        score = json.loads(score)
        db_data = score

        if judge_id is not None:
            # check if user is admin, else he is not allowed to set a judge_id
            roles = cherrypy.session.get(KEY_USER_INFO, {}).get(KEY_ROLES, [])
            if KEY_ROLE_ADMIN not in roles:
                judge_id = None
        if judge_id is None:
            judge_id = cherrypy.session.get(KEY_JUDGE_ID)
            if judge_id is None:
                print 'Error: Not registered as judge'
                return

        db_data['judge_id'] = judge_id

        # TODO: get heat_id for judge_id from state-manager
        heats = cherrypy.engine.publish(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, judge_id).pop()
        active_heat_id = None
        if len(heats) > 0:
            active_heat_id = heats.values()[0][KEY_HEAT_ID]

        if heat_id is None:
            heat_id = active_heat_id

        if heat_id is None:
            print 'Error: No heat_id specified and judge has no active heat'
            return

        if int(heat_id) != int(active_heat_id): # and not is_admin... later: ask for admin roles
            print 'Error: Specified heat_id does not coincide with active heat of judge'
            return

        db_data['heat_id'] = int(heat_id)
        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)
        participants = heat_info['participants']
        color2id = dict(zip(participants['surfer_color'], participants['surfer_id']))
        db_data['surfer_id'] = int(color2id[score['color']])
        del db_data['color']

        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_SCORE, db_data).pop()
        return res


    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_JUDGE, KEY_ROLE_ADMIN))
    def do_modify_score(self, score = None, heat_id = None, judge_id = None):
        if score is None:
            print 'do_modify_score: No score given'
            return

        score = json.loads(score)
        db_data = score

        if judge_id is None:
            judge_id = cherrypy.session.get(KEY_JUDGE_ID)
            if judge_id is None:
                print 'do_modify_score: Not registered as judge and no judge id specified'
                return

        if heat_id is None:
            print 'do_modify_score: No heat_id specified'
            return

        heat_id = int(heat_id)

        db_data['judge_id'] = judge_id

        db_data['heat_id'] = heat_id
        heat_info = self.collect_heat_info(heat_id)
        participants = heat_info['participants']
        color2id = dict(zip(participants['surfer_color'], participants['surfer_id']))
        db_data['surfer_id'] = int(color2id[score['color']])
        del db_data['color']

        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_SCORE, db_data).pop()
        return res


    @cherrypy.expose
    def do_get_active_heat_info(self, heat_id = None, **kwargs):
        if heat_id is not None:
            heat_id = int(heat_id)
        else:
            judge_id = cherrypy.session.get(KEY_JUDGE_ID)
            if judge_id is None:
                print 'Error: Not registered as judge and no heat_id specified'
                return '{}'
            heats = cherrypy.engine.publish(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, judge_id).pop()
            if len(heats) == 0:
                print 'Error: No heat specified and judge has no active heats'
                return '{}'
            heat_id = heats.keys()[0]
        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)
        return json.dumps(heat_info)

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_get_heat_info(self, heat_id = None, **kwargs):
        if heat_id is not None:
            heat_id = int(heat_id)
        else:
            return ''
        heat_info = self.collect_heat_info(heat_id)
        return json.dumps(heat_info)

    @cherrypy.expose
    def do_get_all_active_heats(self, **kwargs):
        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, None).pop()
        return json.dumps(heat_info.values())


    @cherrypy.expose
    @cherrypy.tools.render(template = 'simple_message.html')
    def simple_message(self, msg = None):
        env = {}
        env['message'] = msg
        return env

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def export_scores(self, heat_id=None, n_best_waves=2, mode=None):
        heat_id = int(heat_id)
        query_info = {KEY_HEAT_ID: heat_id}
        scores = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_SCORES, query_info).pop()
        heat_info = self.collect_heat_info(heat_id)#cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)

        id2color = dict(zip(heat_info['participants'].get('surfer_id', []), heat_info['participants'].get('surfer_color', [])))

        judges = set(heat_info.get('judges', []))
        scores_by_surfer_wave = {}
        scores_by_judge_id = {}
        for score in scores:
            if score[KEY_JUDGE_ID] not in judges:
                continue
            scores_by_surfer_wave.setdefault(score['surfer_id'], {}).setdefault(score['wave'], {})[score[KEY_JUDGE_ID]] = score
            scores_by_judge_id.setdefault(score[KEY_JUDGE_ID], {}).setdefault(score['surfer_id'], {})[score['wave']] = score['score']

        average_scores = self._compute_average_scores(scores_by_surfer_wave, judges)
        all_scores, best_scores_by_judge, best_scores_average, sorted_total_scores = self._compute_score_dicts(scores_by_judge_id, average_scores, n_best_waves)

        export_data = self._collect_export_data(all_scores, average_scores, best_scores_by_judge, best_scores_average, sorted_total_scores, heat_info, id2color, n_best_waves)


        heat_name = '{} {} {}'.format(heat_info['tournament_name'], heat_info['category_name'], heat_info['heat_name'])
        directory = 'exports'
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = None
        if mode == 'judge_sheet':
            filename = 'export_{}_heat_sheet.csv'.format(heat_name)
        elif mode == 'best_waves':
            filename = 'export_{}_best_judge_waves.csv'.format(heat_name)
        elif mode == 'averaged_scores':
            filename = 'export_{}_best_average_waves.csv'.format(heat_name)

        if filename is not None:
            utils.write_csv(os.path.join(directory, filename), export_data[mode]['data'], export_data[mode]['header'])

        filename = os.path.abspath(os.path.join(directory, 'Auswertung_{}.xlsx'.format(heat_name)))
        print filename
        utils.write_xlsx(filename, export_data)
        from cherrypy.lib.static import serve_file
        return serve_file(filename, "application/x-download", "attachment")



    def _compute_average_scores(self, scores_by_surfer_wave, judges):
        average_scores = {}
        for surfer_id, data in scores_by_surfer_wave.items():
            for wave, judge_data in data.items():
                if set(judge_data.keys()) != judges:
                    print 'export_scores: not all judges gave score for wave {} of surfer {} --> ignoring'.format(wave, surfer_id)
                    continue

                s = []
                n_missed_scores = 0
                for judge_id, score_data in judge_data.items():
                    if score_data['score'] == VAL_MISSED:
                        n_missed_scores += 1
                    else:
                        s.append(score_data['score'])

                if n_missed_scores > 0:
                    if len(s) == 0:
                        print 'export_scores: WARNING: everyone missed the score'
                        s = [-5] * n_missed_scores
                    else:
                        pre_average = float(sum(s)) / len(s)
                        s.extend([pre_average] * n_missed_scores)

                if len(s) > 3:
                    s = sorted(s)[1:-1]

                final_average = float(sum(s)) / len(s)
                average_scores.setdefault(surfer_id, {})[wave] = final_average
        return average_scores




    def _compute_score_dicts(self, scores_by_judge_id, average_scores, n_best_waves):
        best_scores_by_judge = {}
        best_scores_average = {}
        all_scores = {}
        for surfer_id, data in average_scores.items():
            best_scores_average.setdefault(surfer_id, {})['average'] = sorted(data.items(), key=lambda x: x[1], reverse=True)[:n_best_waves]
            for judge_id in scores_by_judge_id:
                vals = scores_by_judge_id[judge_id][surfer_id]
                best_scores_by_judge.setdefault(surfer_id, {})[judge_id] = sorted(vals.items(), key=lambda x: x[1], reverse=True)[:n_best_waves]
                all_scores.setdefault(surfer_id, {})[judge_id] = sorted(vals.items(), key=lambda x: x[0])

        total_scores = []
        for surfer_id, data in best_scores_average.items():
            wave_idx, scores = zip(*data['average'])
            total_scores.append( (surfer_id, sum(scores)) )
        s = sorted(total_scores, key=lambda x: x[1], reverse=True)
        sorted_total_scores = {}
        for idx, (surfer_id, score) in enumerate(s):
            sorted_total_scores[surfer_id] = (idx, score)
        return all_scores, best_scores_by_judge, best_scores_average, sorted_total_scores


    def _collect_export_data(self, all_scores, average_scores, best_scores_by_judge, best_scores_average, sorted_total_scores, heat_info, id2color, n_best_waves):
        export_data = {}


        # *****************
        # export heat sheet
        # *****************
        csv_out_data = []
        labels_scores = ['Wave {}'.format(i+1) for i in range(heat_info['number_of_waves'])]
        header = ['Name', 'Color', 'Judge Id'] + labels_scores
        highlights = {}
        for idx, surfer_id in enumerate(heat_info['participants']['surfer_id']):
            data = all_scores.get(surfer_id, {})
            for judge_id in heat_info['judges']:
                vals = data.get(judge_id, [])
                res = {}
                res['Judge Id'] = judge_id
                res['Color'] = id2color.get(surfer_id, 'Error: Color not found')
                if len(vals) > 0:
                    indices, scores = zip(*vals)
                else:
                    indices = [None] * n_best_waves
                    scores = [None] * n_best_waves
                best_waves = zip(*best_scores_by_judge.get(surfer_id, {}).get(judge_id, []))
                for label_score, wave_idx, score in zip(labels_scores, indices, scores):
                    res[label_score] = score
                    if len(best_waves) > 0 and wave_idx in best_waves[0]:
                        highlights.setdefault(res['Color'], {}).setdefault(judge_id, []).append( labels_scores[wave_idx] )

                res['Name'] = '{}'.format(heat_info['participants']['name'][idx])
                csv_out_data.append(res)
        export_data.setdefault('judge_sheet', {})['title_line'] = '{} {} {}'.format(heat_info['tournament_name'], heat_info['category_name'], heat_info['heat_name'])
        export_data.setdefault('judge_sheet', {})['header'] = header
        export_data['judge_sheet']['data'] = csv_out_data
        export_data['judge_sheet']['highlights'] = highlights


        # *****************
        # export best waves per judge
        # *****************
        base_data = best_scores_by_judge

        csv_out_data = []
        labels_scores = ['Wave {} (score)'.format(i+1) for i in range(n_best_waves)]
        labels_index = ['Wave {} (number)'.format(i+1) for i in range(n_best_waves)]
        header = ['Name', 'Color', 'Judge Id'] + labels_scores + labels_index
        for idx, surfer_id in enumerate(heat_info['participants']['surfer_id']):
            data = base_data.get(surfer_id, {})
            for judge_id in heat_info['judges']:
                vals = data.get(judge_id, [])
                res = {}
                res['Judge Id'] = judge_id
                res['Color'] = id2color.get(surfer_id, 'Error: Color not found')
                if len(vals) > 0:
                    indices, scores = zip(*vals)
                else:
                    indices = [None] * n_best_waves
                    scores = [None] * n_best_waves
                for label_index, label_score, index, score in zip(labels_index, labels_scores, indices, scores):
                    res[label_score] = '' if score is None else '{:.2f}'.format(score)
                    res[label_index] = '' if index is None else index + 1
                res['Name'] = '{}'.format(heat_info['participants']['name'][idx])
                csv_out_data.append(res)

        export_data.setdefault('best_waves', {})['header'] = header
        export_data['best_waves']['title_line'] = '{} {} {}'.format(heat_info['tournament_name'], heat_info['category_name'], heat_info['heat_name'])
        export_data['best_waves']['data'] = csv_out_data


        # *****************
        # export averaged scores
        # *****************
        base_data = best_scores_average

        csv_out_data = []
        labels_scores = ['Wave {}'.format(i+1) for i in range(n_best_waves)]
        header = ['Ranking', 'Name', 'Color', 'Total Score'] + labels_scores
        for idx, surfer_id in enumerate(heat_info['participants']['surfer_id']):
            data = base_data.get(surfer_id, {})
            vals = data.get('average', [])
            res = {}
            res['Color'] = id2color.get(surfer_id, 'Error: Color not found')
            if len(vals) > 0:
                _, scores = zip(*vals)
                total_score = sum(scores)
            else:
                scores = [None] * n_best_waves
                total_score = 0.0
            for label_score, score in zip(labels_scores, scores):
                res[label_score] = '' if score is None else '{:.2f}'.format(score)
            ranking, total_score = sorted_total_scores.get(surfer_id, (len(heat_info['participants']['surfer_id']) - 1, total_score) )
            res['Name'] = '{}'.format(heat_info['participants']['name'][idx])
            res['Ranking'] = ranking
            res['Total Score'] = total_score
            csv_out_data.append( res )

        export_data.setdefault('averaged_scores', {})['header'] = header
        export_data['averaged_scores']['title_line'] = '{} {} {}'.format(heat_info['tournament_name'], heat_info['category_name'], heat_info['heat_name'])
        export_data['averaged_scores']['data'] = csv_out_data

        return export_data

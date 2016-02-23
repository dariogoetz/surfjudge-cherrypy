from keys import *

def compute_average_scores(scores_by_surfer_wave, judges):
    average_scores = {}
    for surfer_id, data in scores_by_surfer_wave.items():
        for wave, judge_data in data.items():
            if set(judge_data.keys()) != judges:
                print 'score_processing: not all judges gave score for wave {} of surfer {} --> ignoring'.format(wave, surfer_id)
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
                    print 'score_processing: WARNING: everyone missed the score'
                    s = [-5] * n_missed_scores
                else:
                    pre_average = float(sum(s)) / len(s)
                    s.extend([pre_average] * n_missed_scores)

            if len(s) > 4:
                s = sorted(s)[1:-1]

            final_average = float(sum(s)) / len(s)
            average_scores.setdefault(surfer_id, {})[wave] = final_average
    return average_scores



def compute_places_total_scores(average_scores, n_best_waves):
    total_scores = {}
    for surfer_id, data in average_scores.items():
        total_scores[surfer_id] = sum(sorted(data.values(), reverse=True)[:n_best_waves])
    s = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
    sorted_total_scores = {}
    for idx, (surfer_id, score) in enumerate(s):
        sorted_total_scores[surfer_id] = (idx, score)
    return sorted_total_scores


def compute_best_waves(average_scores, n_best_waves):
    best_scores_average = {}
    for surfer_id, data in average_scores.items():
        best_scores_average[surfer_id] = sorted(data.items(), key=lambda x: x[1], reverse=True)[:n_best_waves]
    return best_scores_average


def compute_by_judge_scores(scores_by_surfer_wave, n_best_waves):
    best_scores_by_judge = {}
    all_scores = {}
    for surfer_id, data in scores_by_surfer_wave.items():

        judge_vals = {}
        for wave_idx, scores in data.items():
            for judge_id, score in scores.items():
                judge_vals.setdefault(judge_id, []).append( (wave_idx, score['score'])  )

        for judge_id, vals in judge_vals.items():
            best_scores_by_judge.setdefault(surfer_id, {})[judge_id] = sorted(vals, key=lambda x: x[1], reverse=True)[:n_best_waves]
            all_scores.setdefault(surfer_id, {})[judge_id] = sorted(vals, key=lambda x: x[0])

    return all_scores, best_scores_by_judge


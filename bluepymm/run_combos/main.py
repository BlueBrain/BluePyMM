""" Calculate scores."""

from . import calculate_scores


def run(final_dict, emodel_dirs, scores_db_path, use_ipyp, ipyp_profile):
    print('Calculating scores')
    # Calculate scores for combinations in sqlite3 db
    calculate_scores.calculate_scores(
        final_dict,
        emodel_dirs,
        scores_db_path,
        use_ipyp=use_ipyp,
        ipyp_profile=ipyp_profile)

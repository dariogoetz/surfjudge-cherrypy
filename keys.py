
VAL_MISSED = -1
VAL_INTERFERENCE = -2

#########
# roles #
#########

KEY_ROLES = 'roles'
KEY_ROLE_ADMIN = 'ac_admin'
KEY_ROLE_JUDGE = 'ac_judge'
KEY_ROLE_HEADJUDGE = 'ac_headjudge'
KEY_ROLE_OBSERVER = 'ac_observer'
KEY_ROLE_COMMENTATOR = 'ac_commentator'

################
# user manager #
################

KEY_PASSWORD = 'password'



############
# cherrypy #
############

KEY_USERNAME = '_cp_username'
KEY_USER_INFO = '_cp_user_info'
KEY_JUDGE_ID = '_cp_judge_id'

################################
# cherrypy plugins - user auth #
################################

KEY_ENGINE_USER_LOGIN = 'login-user'
KEY_ENGINE_USER_LOGOUT = 'logout-user'
KEY_ENGINE_USER_REGISTER = 'register-user'
KEY_ENGINE_USER_INFO = 'lookup-user-info'
KEY_ENGINE_USER_ADD_ROLE = 'add-role-user'
KEY_ENGINE_USER_REMOVE_ROLE = 'remove-role-user'
KEY_ENGINE_USER_GET_USERS = 'get-users'


################################
# cherrypy plugins - db access #
################################

KEY_ENGINE_DB_RETRIEVE_SCORES = 'db_retrieve_scores'
KEY_ENGINE_DB_INSERT_SCORE = 'db_insert_score'
KEY_ENGINE_DB_DELETE_SCORE = 'db_delete_score'

KEY_ENGINE_DB_RETRIEVE_TOURNAMENTS = 'db_retrieve_tournaments'
KEY_ENGINE_DB_INSERT_TOURNAMENT = 'db_insert_tournament'
KEY_ENGINE_DB_DELETE_TOURNAMENT = 'db_delete_tournament'

KEY_ENGINE_DB_RETRIEVE_CATEGORIES = 'db_retrieve_categories'
KEY_ENGINE_DB_INSERT_CATEGORY = 'db_insert_category'
KEY_ENGINE_DB_DELETE_CATEGORY = 'db_delete_category'

KEY_ENGINE_DB_RETRIEVE_HEATS = 'db_retrieve_heats'
KEY_ENGINE_DB_INSERT_HEAT = 'db_insert_heat'
KEY_ENGINE_DB_DELETE_HEAT = 'db_delete_heat'

KEY_ENGINE_DB_RETRIEVE_JUDGE_ID_FOR_USERNAME = 'db_retrieve_judge_id'

KEY_ENGINE_DB_RETRIEVE_SURFERS = 'db_retrieve_surfers'
KEY_ENGINE_DB_INSERT_SURFER = 'db_insert_surfer'
KEY_ENGINE_DB_DELETE_SURFER = 'db_delete_surfer'

KEY_ENGINE_DB_RETRIEVE_PARTICIPANTS = 'db_retrieve_participants'
KEY_ENGINE_DB_SET_PARTICIPANTS = 'db_set_participants'

KEY_ENGINE_DB_RETRIEVE_JUDGES = 'db_retrieve_judges'
KEY_ENGINE_DB_INSERT_JUDGE = 'db_insert_judge'
KEY_ENGINE_DB_DELETE_JUDGE = 'db_delete_judge'

KEY_ENGINE_DB_RETRIEVE_JUDGE_ACTIVITIES = 'db_retrieve_judge_activities'
KEY_ENGINE_DB_SET_JUDGE_ACTIVITIES = 'db_set_judge_activities'
KEY_ENGINE_DB_DELETE_JUDGE_ACTIVITY = 'db_delete_judge_activity'
KEY_ENGINE_DB_RETRIEVE_JUDGES_FOR_HEAT = 'db_retrieve_judges_for_heat'
KEY_ENGINE_DB_RETRIEVE_HEAT_INFO = 'db_retrieve_heat_info'
KEY_ENGINE_DB_RETRIEVE_RESULTS = 'db_retrieve_results'
KEY_ENGINE_DB_INSERT_RESULT = 'db_insert_result'
KEY_ENGINE_DB_DELETE_RESULTS = 'db_delete_results'

##########################################
# cherrypy plugins - statemanager access #
##########################################

KEY_ENGINE_SM_ACTIVATE_HEAT = 'sm_activate_heat'
KEY_ENGINE_SM_DEACTIVATE_HEAT = 'sm_deactivate_heat'
KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO = 'sm_get_active_heat_info'
KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE = 'sm_get_heats_for_judge'


################################################
# cherrypy plugins - tournament_manager access #
################################################


KEY_ENGINE_TM_GET_HEAT_ORDER = 'tm_get_heat_order'
KEY_ENGINE_TM_SET_HEAT_ORDER = 'tm_set_heat_order'
KEY_ENGINE_TM_GET_CURRENT_HEAT_ID = 'tm_get_current_heat_id'
KEY_ENGINE_TM_SET_CURRENT_HEAT_ID = 'tm_set_current_heat_id'
KEY_ENGINE_TM_GET_ADVANCING_SURFERS = 'tm_get_advancing_surfers'
KEY_ENGINE_TM_SET_ADVANCING_SURFER = 'tm_set_advancing_surfer'
KEY_ENGINE_TM_GENERATE_HEATS = 'tm_generate_heats'


#############################################
# cherrypy plugins - judging_manager access #
#############################################

KEY_ENGINE_JM_REGISTER_JUDGING_REQUEST = 'jm_register_judging_request'
KEY_ENGINE_JM_UNREGISTER_JUDGING_REQUEST = 'jm_unregister_judging_request'
KEY_ENGINE_JM_GET_JUDGING_REQUESTS = 'jm_get_judging_requests'


###################################
# cherrypy plugins - jinja lookup #
###################################

KEY_ENGINE_LOOKUP_TEMPLATE = 'lookup-template'


############
# database #
############

KEY_SHUTDOWN = 'shutdown'


#################
# state manager #
#################

KEY_TOURNAMENT_NAME = 'tournament_name'
KEY_CLASS_NAME      = 'class_name'
KEY_EVENT_NAME      = 'event_name'
KEY_HEAT_ID         = 'heat_id'
KEY_HEAT_NAME       = 'heat_name'
KEY_JUDGE_ID        = 'judge_id'




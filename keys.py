
#########
# roles #
#########

KEY_ROLES = 'roles'
KEY_ROLE_ADMIN = 'ac_admin'
KEY_ROLE_JUDGE = 'ac_judge'
KEY_ROLE_HEADJUDGE = 'ac_headjudge'
KEY_ROLE_OBSERVER = 'ac_observer'


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


################################
# cherrypy plugins - db access #
################################

KEY_ENGINE_DB_RETRIEVE_SCORES = 'db_retrieve_scores'
KEY_ENGINE_DB_INSERT_SCORE = 'db_insert_score'
KEY_ENGINE_DB_RETRIEVE_TOURNAMENTS = 'db_retrieve_tournaments'
KEY_ENGINE_DB_INSERT_TOURNAMENT = 'db_insert_tournament'
KEY_ENGINE_DB_DELETE_TOURNAMENT = 'db_delete_tournament'
KEY_ENGINE_DB_RETRIEVE_HEATS = 'db_retrieve_heats'
KEY_ENGINE_DB_INSERT_HEAT = 'db_insert_heat'
KEY_ENGINE_DB_DELETE_HEAT = 'db_delete_heat'
KEY_ENGINE_DB_RETRIEVE_JUDGE_ID = 'db_retrieve_judge_id'
KEY_ENGINE_DB_RETRIEVE_SURFERS = 'db_retrieve_surfers'
KEY_ENGINE_DB_RETRIEVE_JUDGE_ACTIVITIES = 'db_retrieve_judge_activities'

KEY_ENGINE_SM_ACTIVATE_HEAT = 'sm_activate_heat'
KEY_ENGINE_SM_DEACTIVATE_HEAT = 'sm_deactivate_heat'
KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO = 'sm_get_active_heat_info'


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

KEY_TOURNAMENT = 'tournament'
KEY_CLASS      = 'class'
KEY_HEAT_ID       = 'heat_id'
KEY_JUDGE_ID      = 'judge_id'

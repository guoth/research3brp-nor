from os import environ


SESSION_CONFIGS = [
    dict(
        name='public_goods_corrupt_punish',
        display_name="research3brp-nor",
        app_sequence=['public_goods_corrupt_punish'],
        num_demo_participants=4,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, 
    participation_fee=3.00,  # 固定参与费3元
    doc="research2p"
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'zh-hans'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'CNY'
USE_POINTS = True

ROOMS = [
    dict(
        name='experiment_room',
        display_name='实验房间',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(
        name='live_demo', 
        display_name='实时演示（无参与者标签）'
    ),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
欢迎参加实验！
"""


SECRET_KEY = '{{ secret_key }}'

INSTALLED_APPS = ['otree']
import random
import time

from otree.api import *

"""
两套实验逻辑系统说明：
1. 实验固定进行两轮：第1轮运行逻辑1，第2轮运行逻辑2。
2. 当前逻辑2先完整复用逻辑1的流程与页面，便于后续再单独调整第二套逻辑。
3. 在任何页面中，都可以通过 player.current_logic 获取当前轮次的逻辑编号（1或2）。
4. 在 HTML 模板中，可以通过 {% if current_logic == 1 %} 来显示不同内容。
"""


ESTIMATE_ACTUAL_FIELDS = [f'estimate_actual_{i}' for i in range(21)]
ESTIMATE_SHOULD_FIELDS = [f'estimate_should_{i}' for i in range(21)]
COMPREHENSION_FIELDS = [
    'comprehension_q1',
    'comprehension_q2',
    'comprehension_q3',
    'comprehension_q4',
]
COMPREHENSION_CORRECT_ANSWERS = {
    'comprehension_q1': 2,
    'comprehension_q2': 4,
    'comprehension_q3': 3,
    'comprehension_q4': 2,
}
COMPREHENSION_ORDER_KEY = 'comprehension_question_order'


class C(BaseConstants):
    NAME_IN_URL = 'pgcor'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 2
    ENDOWMENT = cu(20)
    MULTIPLIER = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()


class Player(BasePlayer):
    consent = models.BooleanField(label='我已阅读并同意参加本研究')
    subject_id = models.IntegerField(label='请输入你的被试编号：')
    player_role = models.StringField()

    comprehension_q1 = models.IntegerField(
        label='公共池的倍率为多少？',
        choices=[
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
        ],
        widget=widgets.RadioSelect,
    )
    comprehension_q2 = models.IntegerField(
        label='每组中共有几个角色？',
        choices=[
            [1, '2'],
            [2, '3'],
            [3, '4'],
            [4, '5'],
        ],
        widget=widgets.RadioSelect,
    )
    comprehension_q3 = models.IntegerField(
        label='E的1代币可以增加/减少A、B、C或D的多少代币？',
        choices=[
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
        ],
        widget=widgets.RadioSelect,
    )
    comprehension_q4 = models.IntegerField(
        label='如果E获得了A的分配，该E：',
        choices=[
            [1, '仍然可以奖励/惩罚A'],
            [2, '不能惩罚且必须奖励A'],
            [3, '仍然可以奖励/惩罚所有人'],
            [4, '奖惩权不受该分配影响'],
        ],
        widget=widgets.RadioSelect,
    )
    comprehension_error_count = models.IntegerField(initial=0)

    for i in range(21):
        locals()[f'estimate_actual_{i}'] = models.IntegerField(min=0, max=100)
    for i in range(21):
        locals()[f'estimate_should_{i}'] = models.IntegerField(min=0, max=100)
    del i

    contribution = models.IntegerField(
        min=0,
        max=C.ENDOWMENT,
        label='你选择投入公共池的代币数为：',
    )
    transfer_to_e = models.IntegerField(
        min=0,
        max=C.ENDOWMENT,
        label='你选择转给玩家E的代币数为：',
    )
    reaction_time = models.FloatField(initial=0)
    estimate_reaction_time = models.FloatField(initial=0)
    page_load_time = models.FloatField(initial=0)
    research_result_time = models.FloatField(initial=0)
    
    questionnaire_start_time = models.FloatField(initial=0)
    questionnaire_duration = models.FloatField(initial=0)

    emotion_state = models.IntegerField(
        label='此时你的情绪状态为：',
        choices=[
            [1, '1 - 非常消极'],
            [2, '2 - 比较消极'],
            [3, '3 - 有点消极'],
            [4, '4 - 不消极也不积极'],
            [5, '5 - 有点积极'],
            [6, '6 - 比较积极'],
            [7, '7 - 非常积极'],
        ],
        widget=widgets.RadioSelect,
    )

    major = models.StringField(label='1. 您的专业为：')
    major_category = models.IntegerField(
        label='2. 您的专业类别为：',
        choices=[[1, '文科'], [2, '理科'], [3, '工科'], [4, '其他']],
        widget=widgets.RadioSelect,
    )
    student_id = models.StringField(label='3. 您的学号为：')
    gender = models.IntegerField(
        label='4. 您的性别：',
        choices=[[1, '男'], [2, '女']],
        widget=widgets.RadioSelect,
    )
    age = models.IntegerField(label='5. 您的年龄为：')
    education = models.IntegerField(
        label='6. 您的学历：',
        choices=[[1, '大学专科'], [2, '大学本科'], [3, '研究生及以上']],
        widget=widgets.RadioSelect,
    )
    work_experience = models.IntegerField(
        label='7. 您是否有工作经验：包括兼职、寒暑假工与实习',
        choices=[[1, '是'], [2, '否']],
        widget=widgets.RadioSelect,
    )

    is_real_player = models.IntegerField(
        label='1. 您认为此次游戏中的其他玩家是否为真人?',
        choices=[[1, '是真人'], [2, '不是真人']],
        widget=widgets.RadioSelect,
    )
    careful_completion_check = models.IntegerField(
        label='2. 您是否有认真完成实验与问卷，此题选否',
        choices=[[1, '是'], [2, '否']],
        widget=widgets.RadioSelect,
    )
    contribution_decision_priority = models.IntegerField(
        label='4. 在决定向公共池投入多少代币时，我会优先考虑：',
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal,
    )

    question3_1 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7])
    question3_2 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7])
    question3_3 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7])
    question3_4 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7])

    @property
    def role(self):
        return self.player_role

    @property
    def current_logic(self):
        return 1 if self.round_number == 1 else 2


def get_comprehension_question_order(player: Player):
    if player.round_number == 1:
        return COMPREHENSION_FIELDS

    return [
        'comprehension_q2',
        'comprehension_q1',
        'comprehension_q4',
        'comprehension_q3',
    ]


def creating_session(subsession: Subsession):
    roles = ['A', 'B', 'C', 'D']

    if subsession.round_number > 1:
        subsession.group_like_round(1)

    for group in subsession.get_groups():
        players = group.get_players()

        if subsession.round_number == 1:
            assigned_roles = roles.copy()
            random.shuffle(assigned_roles)
            for index, player in enumerate(players):
                player.player_role = assigned_roles[index]
                player.participant.vars['player_role'] = player.player_role
        else:
            for player in players:
                stored_role = player.participant.vars.get('player_role')
                if stored_role:
                    player.player_role = stored_role

        if subsession.round_number > 1:
            for player in players:
                stored_subject_id = player.participant.vars.get('subject_id')
                if stored_subject_id is not None:
                    player.subject_id = stored_subject_id


def set_payoffs(group: Group):
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = (
        group.total_contribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
    )
    for player in players:
        player.payoff = C.ENDOWMENT - player.contribution + group.individual_share


class ConsentPage(Page):
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('consent'):
            return '只有同意参加实验才能进入实验。'


class ParticipantID(Page):
    form_model = 'player'
    form_fields = ['subject_id']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['subject_id'] = player.subject_id


class Instructions(Page):
    pass


class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = COMPREHENSION_FIELDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            ordered_questions=get_comprehension_question_order(player),
            current_logic=player.current_logic,
        )

    @staticmethod
    def error_message(player: Player, values):
        wrong_questions = []
        for field_name, correct_answer in COMPREHENSION_CORRECT_ANSWERS.items():
            if values.get(field_name) != correct_answer:
                wrong_questions.append(field_name)

        if wrong_questions:
            player.comprehension_error_count += len(wrong_questions)
            
            # 获取当前页面的题目显示顺序
            current_order = get_comprehension_question_order(player)
            
            # 根据题目在页面上的实际顺序（索引+1）来提示
            wrong_indices = sorted(current_order.index(field) + 1 for field in wrong_questions)
            wrong_labels = '、'.join(f'第{i}题' for i in wrong_indices)
            
            return f'{wrong_labels}回答错误。请确认规则后重新作答，只有全部答对才能继续。'


class ComprehensionWaitPage(WaitPage):
    title_text = '等待其他玩家'
    body_text = '请稍候，等待其他玩家完成理解检查并加入游戏...'


class MatchingWaitPage(Page):
    timeout_seconds = 4
    title_text = '正在匹配其他玩家'
    body_text = '请稍候，正在为你匹配其他玩家...'


class MatchingSuccess(Page):
    timeout_seconds = 4


class EstimateOthers(Page):
    form_model = 'player'
    form_fields = ESTIMATE_SHOULD_FIELDS + ESTIMATE_ACTUAL_FIELDS + ['estimate_reaction_time']

    @staticmethod
    def error_message(player: Player, values):
        should_sum = sum(values.get(field_name) or 0 for field_name in ESTIMATE_SHOULD_FIELDS)
        actual_sum = sum(values.get(field_name) or 0 for field_name in ESTIMATE_ACTUAL_FIELDS)

        errors = []
        if should_sum != 100:
            errors.append(f'问题（2）的百分比总和为{should_sum}%，应为100%。')
        if actual_sum != 100:
            errors.append(f'问题（1）的百分比总和为{actual_sum}%，应为100%。')
        if errors:
            return ' '.join(errors)


class Contribute(Page):
    form_model = 'player'
    form_fields = ['contribution', 'transfer_to_e', 'reaction_time', 'page_load_time']

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'player_role': player.role,
            'current_logic': player.current_logic,
        }

    @staticmethod
    def error_message(player: Player, values):
        contribution = values.get('contribution', 0) or 0
        transfer_to_e = values.get('transfer_to_e', 0) or 0
        total = contribution + transfer_to_e

        if total > C.ENDOWMENT:
            return (
                f'你投入公共池的代币数（{contribution}）和转给玩家E的代币数'
                f'（{transfer_to_e}）的总和（{total}）不能超过{C.ENDOWMENT}个代币。请重新分配。'
            )


class ResultsWaitPage(WaitPage):
    title_text = '等待其他玩家'
    body_text = '请稍候，等待其他玩家完成决策...'
    after_all_players_arrive = set_payoffs


class PlayerEWaitPage(Page):
    timeout_seconds = 6


class EmotionAssessment(Page):
    form_model = 'player'
    form_fields = ['emotion_state']


class QuestionnaireIntro(Page):
    timeout_seconds = 3

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 2


class QuestionnairePart1(Page):
    form_model = 'player'
    form_fields = [
        'major',
        'major_category',
        'student_id',
        'gender',
        'age',
        'education',
        'work_experience',
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 2

    @staticmethod
    def vars_for_template(player: Player):
        if player.questionnaire_start_time == 0:
            player.questionnaire_start_time = time.time()
        return dict()


class QuestionnairePart2(Page):
    form_model = 'player'
    form_fields = ['is_real_player', 'careful_completion_check', 'question3_1', 'question3_2', 'question3_3', 'question3_4', 'contribution_decision_priority']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 2

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.questionnaire_start_time > 0:
            player.questionnaire_duration = time.time() - player.questionnaire_start_time


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        stored_subject_id = player.field_maybe_none('subject_id')
        if stored_subject_id is None:
            stored_subject_id = player.participant.vars.get('subject_id')
            if stored_subject_id is not None:
                player.subject_id = stored_subject_id
        return dict(subject_id=stored_subject_id)


class ThankYou(Page):
    pass


class Researchresult(Page):
    form_model = 'player'
    form_fields = ['research_result_time']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 2


class LoadingNextTask(Page):
    pass


page_sequence = [
    ConsentPage,
    ParticipantID,
    Instructions,
    ComprehensionCheck,
    ComprehensionWaitPage,
    MatchingWaitPage,
    MatchingSuccess,
    Researchresult,
    LoadingNextTask,
    EstimateOthers,
    Contribute,
    ResultsWaitPage,
    PlayerEWaitPage,
    QuestionnaireIntro,
    QuestionnairePart1,
    QuestionnairePart2,
    Results,
]

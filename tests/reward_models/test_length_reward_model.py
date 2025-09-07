from codex_ml.reward_models import LengthRewardModel


def test_length_reward_model_basic():
    rm = LengthRewardModel()
    short = rm.evaluate("p", "hi")
    long = rm.evaluate("p", "hello")
    assert long > short


def test_length_reward_model_batch_and_learn():
    rm = LengthRewardModel()
    scores = rm.batch_evaluate([("p", "ab"), ("p", "abcd")])
    assert scores == [2.0, 4.0]
    metrics = rm.learn([("p", "a")])
    assert metrics == {"loss": 0.0}

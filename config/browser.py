# -*- coding:utf-8 -*-
# Desc: project app configuration
"""
"""
from utils import env, template


class BrowserConf:
    browser_user = {
        # TODO ID 固定且唯一。 用于链接浏览器的name 非测试模式，请关闭第一个
        "9600": {
            "status": env("BROWSER_STATUS_9600", "disabled"),
            "port": 9600,
        },
        "9601": {
            "status": env("BROWSER_STATUS_9601", "disabled"),
            "port": 9601,
        },
        "9602": {
            "status": env("BROWSER_STATUS_9602", "disabled"),
            "port": 9602,
        },
        "9603": {
            "status": env("BROWSER_STATUS_9603", "disabled"),
            "port": 9603,
        },
        "9604": {
            "status": env("BROWSER_STATUS_9604", "disabled"),
            "port": 9604,
        },
        "9605": {
            "status": env("BROWSER_STATUS_9605", "disabled"),
            "port": 9605,
        },
        "9606": {
            "status": env("BROWSER_STATUS_9606", "disabled"),
            "port": 9606,
        },
        "9607": {
            "status": env("BROWSER_STATUS_9607", "disabled"),
            "port": 9607,
        },
        "9608": {
            "status": env("BROWSER_STATUS_9608", "disabled"),
            "port": 9608,
        },
        "9609": {
            "status": env("BROWSER_STATUS_9609", "disabled"),
            "port": 9609,
        },
        "9610": {
            "status": env("BROWSER_STATUS_9610", "disabled"),
            "port": 9610,
        },
        "9611": {
            "status": env("BROWSER_STATUS_9611", "disabled"),
            "port": 9611,
        },
        "9612": {
            "status": env("BROWSER_STATUS_9612", "disabled"),
            "port": 9612,
        },
        "9613": {
            "status": env("BROWSER_STATUS_9613", "disabled"),
            "port": 9613,
        },
        "9614": {
            "status": env("BROWSER_STATUS_9614", "disabled"),
            "port": 9614,
        },
        "9615": {
            "status": env("BROWSER_STATUS_9615", "disabled"),
            "port": 9615,
        },
        "9616": {
            "status": env("BROWSER_STATUS_9616", "disabled"),
            "port": 9616,
        },
        "9617": {
            "status": env("BROWSER_STATUS_9617", "disabled"),
            "port": 9617,
        },
        "9618": {
            "status": env("BROWSER_STATUS_9618", "disabled"),
            "port": 9618,
        },
        "9619": {
            "status": env("BROWSER_STATUS_9619", "disabled"),
            "port": 9619,
        },
        "9620": {
            "status": env("BROWSER_STATUS_9620", "disabled"),
            "port": 9620,
        },
        "9621": {
            "status": env("BROWSER_STATUS_9621", "disabled"),
            "port": 9621,
        },
        "9622": {
            "status": env("BROWSER_STATUS_9622", "disabled"),
            "port": 9622,
        },
        "9623": {
            "status": env("BROWSER_STATUS_9623", "disabled"),
            "port": 9623,
        },
        "9624": {
            "status": env("BROWSER_STATUS_9624", "disabled"),
            "port": 9624,
        },
        "9625": {
            "status": env("BROWSER_STATUS_9625", "disabled"),
            "port": 9625,
        },
        "9626": {
            "status": env("BROWSER_STATUS_9626", "disabled"),
            "port": 9626,
        },
        "9627": {
            "status": env("BROWSER_STATUS_9627", "disabled"),
            "port": 9627,
        },
        "9628": {
            "status": env("BROWSER_STATUS_9628", "disabled"),
            "port": 9628,
        },
        "9629": {
            "status": env("BROWSER_STATUS_9629", "disabled"),
            "port": 9629,
        },
        "9630": {
            "status": env("BROWSER_STATUS_9630", "disabled"),
            "port": 9630,
        },
        "9631": {
            "status": env("BROWSER_STATUS_9631", "disabled"),
            "port": 9631,
        },
        "9632": {
            "status": env("BROWSER_STATUS_9632", "disabled"),
            "port": 9632,
        },
        "9633": {
            "status": env("BROWSER_STATUS_9633", "disabled"),
            "port": 9633,
        },
        "9634": {
            "status": env("BROWSER_STATUS_9634", "disabled"),
            "port": 9634,
        },
        "9635": {
            "status": env("BROWSER_STATUS_9635", "disabled"),
            "port": 9635,
        },
        "9636": {
            "status": env("BROWSER_STATUS_9636", "disabled"),
            "port": 9636,
        },
        "9637": {
            "status": env("BROWSER_STATUS_9637", "disabled"),
            "port": 9637,
        },
        "9638": {
            "status": env("BROWSER_STATUS_9638", "disabled"),
            "port": 9638,
        },
        "9639": {
            "status": env("BROWSER_STATUS_9639", "disabled"),
            "port": 9639,
        },
        "9640": {
            "status": env("BROWSER_STATUS_9640", "disabled"),
            "port": 9640,
        },
        "9641": {
            "status": env("BROWSER_STATUS_9641", "disabled"),
            "port": 9641,
        },
        "9642": {
            "status": env("BROWSER_STATUS_9642", "disabled"),
            "port": 9642,
        },
        "9643": {
            "status": env("BROWSER_STATUS_9643", "disabled"),
            "port": 9643,
        },
        "9644": {
            "status": env("BROWSER_STATUS_9644", "disabled"),
            "port": 9644,
        },
        "9645": {
            "status": env("BROWSER_STATUS_9645", "disabled"),
            "port": 9645,
        },
        "9646": {
            "status": env("BROWSER_STATUS_9646", "disabled"),
            "port": 9646,
        },
        "9647": {
            "status": env("BROWSER_STATUS_9647", "disabled"),
            "port": 9647,
        },
        "9648": {
            "status": env("BROWSER_STATUS_9648", "disabled"),
            "port": 9648,
        },
        "9649": {
            "status": env("BROWSER_STATUS_9649", "disabled"),
            "port": 9649,
        },
        # 第二集团军
        "9650": {
            "status": env("BROWSER_STATUS_9650", "disabled"),
            "port": 9650,
        },
        "9651": {
            "status": env("BROWSER_STATUS_9651", "disabled"),
            "port": 9651,
        },
        "9652": {
            "status": env("BROWSER_STATUS_9652", "disabled"),
            "port": 9652,
        },
        "9653": {
            "status": env("BROWSER_STATUS_9653", "disabled"),
            "port": 9653,
        },
        "9654": {
            "status": env("BROWSER_STATUS_9654", "disabled"),
            "port": 9654,
        },
        "9655": {
            "status": env("BROWSER_STATUS_9655", "disabled"),
            "port": 9655,
        },
        "9656": {
            "status": env("BROWSER_STATUS_9656", "disabled"),
            "port": 9656,
        },
        "9657": {
            "status": env("BROWSER_STATUS_9657", "disabled"),
            "port": 9657,
        },
        "9658": {
            "status": env("BROWSER_STATUS_9658", "disabled"),
            "port": 9658,
        },
        "9659": {
            "status": env("BROWSER_STATUS_9659", "disabled"),
            "port": 9659,
        },
        "9660": {
            "status": env("BROWSER_STATUS_9660", "disabled"),
            "port": 9660,
        },
        "9661": {
            "status": env("BROWSER_STATUS_9661", "disabled"),
            "port": 9661,
        },
        "9662": {
            "status": env("BROWSER_STATUS_9662", "disabled"),
            "port": 9662,
        },
        "9663": {
            "status": env("BROWSER_STATUS_9663", "disabled"),
            "port": 9663,
        },
        "9664": {
            "status": env("BROWSER_STATUS_9664", "disabled"),
            "port": 9664,
        },
        "9665": {
            "status": env("BROWSER_STATUS_9665", "disabled"),
            "port": 9665,
        },
        "9666": {
            "status": env("BROWSER_STATUS_9666", "disabled"),
            "port": 9666,
        },
        "9667": {
            "status": env("BROWSER_STATUS_9667", "disabled"),
            "port": 9667,
        },
        "9668": {
            "status": env("BROWSER_STATUS_9668", "disabled"),
            "port": 9668,
        },
        "9669": {
            "status": env("BROWSER_STATUS_9669", "disabled"),
            "port": 9669,
        },
        "9670": {
            "status": env("BROWSER_STATUS_9670", "disabled"),
            "port": 9670,
        },
        "9671": {
            "status": env("BROWSER_STATUS_9671", "disabled"),
            "port": 9671,
        },
        "9672": {
            "status": env("BROWSER_STATUS_9672", "disabled"),
            "port": 9672,
        },
        "9673": {
            "status": env("BROWSER_STATUS_9673", "disabled"),
            "port": 9673,
        },
        "9674": {
            "status": env("BROWSER_STATUS_9674", "disabled"),
            "port": 9674,
        },
        "9675": {
            "status": env("BROWSER_STATUS_9675", "disabled"),
            "port": 9675,
        },
        "9676": {
            "status": env("BROWSER_STATUS_9676", "disabled"),
            "port": 9676,
        },
        "9677": {
            "status": env("BROWSER_STATUS_9677", "disabled"),
            "port": 9677,
        },
        "9678": {
            "status": env("BROWSER_STATUS_9678", "disabled"),
            "port": 9678,
        },
        "9679": {
            "status": env("BROWSER_STATUS_9679", "disabled"),
            "port": 9679,
        },
        "9680": {
            "status": env("BROWSER_STATUS_9680", "disabled"),
            "port": 9680,
        },
        "9681": {
            "status": env("BROWSER_STATUS_9681", "disabled"),
            "port": 9681,
        },
        "9682": {
            "status": env("BROWSER_STATUS_9682", "disabled"),
            "port": 9682,
        },
        "9683": {
            "status": env("BROWSER_STATUS_9683", "disabled"),
            "port": 9683,
        },
        "9684": {
            "status": env("BROWSER_STATUS_9684", "disabled"),
            "port": 9684,
        },
        "9685": {
            "status": env("BROWSER_STATUS_9685", "disabled"),
            "port": 9685,
        },
        "9686": {
            "status": env("BROWSER_STATUS_9686", "disabled"),
            "port": 9686,
        },
        "9687": {
            "status": env("BROWSER_STATUS_9687", "disabled"),
            "port": 9687,
        },
        "9688": {
            "status": env("BROWSER_STATUS_9688", "disabled"),
            "port": 9688,
        },
        "9689": {
            "status": env("BROWSER_STATUS_9689", "disabled"),
            "port": 9689,
        },
        "9690": {
            "status": env("BROWSER_STATUS_9690", "disabled"),
            "port": 9690,
        },
        "9691": {
            "status": env("BROWSER_STATUS_9691", "disabled"),
            "port": 9691,
        },
        "9692": {
            "status": env("BROWSER_STATUS_9692", "disabled"),
            "port": 9692,
        },
        "9693": {
            "status": env("BROWSER_STATUS_9693", "disabled"),
            "port": 9693,
        },
        "9694": {
            "status": env("BROWSER_STATUS_9694", "disabled"),
            "port": 9694,
        },
        # 第三集团军
        "9700": {
            "status": env("BROWSER_STATUS_9700", "disabled"),
            "port": 9700,
        },
        "9701": {
            "status": env("BROWSER_STATUS_9701", "disabled"),
            "port": 9701,
        },
        "9702": {
            "status": env("BROWSER_STATUS_9702", "disabled"),
            "port": 9702,
        },
        "9703": {
            "status": env("BROWSER_STATUS_9703", "disabled"),
            "port": 9703,
        },
        "9704": {
            "status": env("BROWSER_STATUS_9704", "disabled"),
            "port": 9704,
        },
        "9705": {
            "status": env("BROWSER_STATUS_9705", "disabled"),
            "port": 9705,
        },
        "9706": {
            "status": env("BROWSER_STATUS_9706", "disabled"),
            "port": 9706,
        },
        "9707": {
            "status": env("BROWSER_STATUS_9707", "disabled"),
            "port": 9707,
        },
        "9708": {
            "status": env("BROWSER_STATUS_9708", "disabled"),
            "port": 9708,
        },
        "9709": {
            "status": env("BROWSER_STATUS_9709", "disabled"),
            "port": 9709,
        },
        "9710": {
            "status": env("BROWSER_STATUS_9710", "disabled"),
            "port": 9710,
        },
        "9711": {
            "status": env("BROWSER_STATUS_9711", "disabled"),
            "port": 9711,
        },
        "9712": {
            "status": env("BROWSER_STATUS_9712", "disabled"),
            "port": 9712,
        },
        "9713": {
            "status": env("BROWSER_STATUS_9713", "disabled"),
            "port": 9713,
        },
        "9714": {
            "status": env("BROWSER_STATUS_9714", "disabled"),
            "port": 9714,
        },
        "9715": {
            "status": env("BROWSER_STATUS_9715", "disabled"),
            "port": 9715,
        },
        "9716": {
            "status": env("BROWSER_STATUS_9716", "disabled"),
            "port": 9716,
        },
        "9717": {
            "status": env("BROWSER_STATUS_9717", "disabled"),
            "port": 9717,
        },
        "9718": {
            "status": env("BROWSER_STATUS_9718", "disabled"),
            "port": 9718,
        },
        "9719": {
            "status": env("BROWSER_STATUS_9719", "disabled"),
            "port": 9719,
        },
        "9720": {
            "status": env("BROWSER_STATUS_9720", "disabled"),
            "port": 9720,
        },
        "9721": {
            "status": env("BROWSER_STATUS_9721", "disabled"),
            "port": 9721,
        },
        "9722": {
            "status": env("BROWSER_STATUS_9722", "disabled"),
            "port": 9722,
        },
        "9723": {
            "status": env("BROWSER_STATUS_9723", "disabled"),
            "port": 9723,
        },
        "9724": {
            "status": env("BROWSER_STATUS_9724", "disabled"),
            "port": 9724,
        },
        "9725": {
            "status": env("BROWSER_STATUS_9725", "disabled"),
            "port": 9725,
        },
        "9726": {
            "status": env("BROWSER_STATUS_9726", "disabled"),
            "port": 9726,
        },
        "9727": {
            "status": env("BROWSER_STATUS_9727", "disabled"),
            "port": 9727,
        },
        "9728": {
            "status": env("BROWSER_STATUS_9728", "disabled"),
            "port": 9728,
        },
        "9729": {
            "status": env("BROWSER_STATUS_9729", "disabled"),
            "port": 9729,
        },
        "9730": {
            "status": env("BROWSER_STATUS_9730", "disabled"),
            "port": 9730,
        },
        "9731": {
            "status": env("BROWSER_STATUS_9731", "disabled"),
            "port": 9731,
        },
        "9732": {
            "status": env("BROWSER_STATUS_9732", "disabled"),
            "port": 9732,
        },
        "9733": {
            "status": env("BROWSER_STATUS_9733", "disabled"),
            "port": 9733,
        },
        "9734": {
            "status": env("BROWSER_STATUS_9734", "disabled"),
            "port": 9734,
        },
        "9735": {
            "status": env("BROWSER_STATUS_9735", "disabled"),
            "port": 9735,
        },
        "9736": {
            "status": env("BROWSER_STATUS_9736", "disabled"),
            "port": 9736,
        },
        "9737": {
            "status": env("BROWSER_STATUS_9737", "disabled"),
            "port": 9737,
        },
        "9738": {
            "status": env("BROWSER_STATUS_9738", "disabled"),
            "port": 9738,
        },
        "9739": {
            "status": env("BROWSER_STATUS_9739", "disabled"),
            "port": 9739,
        },
        "9740": {
            "status": env("BROWSER_STATUS_9740", "disabled"),
            "port": 9740,
        },
        "9741": {
            "status": env("BROWSER_STATUS_9741", "disabled"),
            "port": 9741,
        },
        "9742": {
            "status": env("BROWSER_STATUS_9742", "disabled"),
            "port": 9742,
        },
        "9743": {
            "status": env("BROWSER_STATUS_9743", "disabled"),
            "port": 9743,
        },
        "9744": {
            "status": env("BROWSER_STATUS_9744", "disabled"),
            "port": 9744,
        },
        "9745": {
            "status": env("BROWSER_STATUS_9745", "disabled"),
            "port": 9745,
        },
        "9746": {
            "status": env("BROWSER_STATUS_9746", "disabled"),
            "port": 9746,
        },
        "9747": {
            "status": env("BROWSER_STATUS_9747", "disabled"),
            "port": 9747,
        },
        "9748": {
            "status": env("BROWSER_STATUS_9748", "disabled"),
            "port": 9748,
        },
        "9749": {
            "status": env("BROWSER_STATUS_9749", "disabled"),
            "port": 9749,
        },
        # 第二集团军
        "9750": {
            "status": env("BROWSER_STATUS_9750", "disabled"),
            "port": 9750,
        },
        "9751": {
            "status": env("BROWSER_STATUS_9751", "disabled"),
            "port": 9751,
        },
        "9752": {
            "status": env("BROWSER_STATUS_9752", "disabled"),
            "port": 9752,
        },
        "9753": {
            "status": env("BROWSER_STATUS_9753", "disabled"),
            "port": 9753,
        },
        "9754": {
            "status": env("BROWSER_STATUS_9754", "disabled"),
            "port": 9754,
        },
        "9755": {
            "status": env("BROWSER_STATUS_9755", "disabled"),
            "port": 9755,
        },
        "9756": {
            "status": env("BROWSER_STATUS_9756", "disabled"),
            "port": 9756,
        },
        "9757": {
            "status": env("BROWSER_STATUS_9757", "disabled"),
            "port": 9757,
        },
        "9758": {
            "status": env("BROWSER_STATUS_9758", "disabled"),
            "port": 9758,
        },
        "9759": {
            "status": env("BROWSER_STATUS_9759", "disabled"),
            "port": 9759,
        },
        "9760": {
            "status": env("BROWSER_STATUS_9760", "disabled"),
            "port": 9760,
        },
        "9761": {
            "status": env("BROWSER_STATUS_9761", "disabled"),
            "port": 9761,
        },
        "9762": {
            "status": env("BROWSER_STATUS_9762", "disabled"),
            "port": 9762,
        },
        "9763": {
            "status": env("BROWSER_STATUS_9763", "disabled"),
            "port": 9763,
        },
        "9764": {
            "status": env("BROWSER_STATUS_9764", "disabled"),
            "port": 9764,
        },
        "9765": {
            "status": env("BROWSER_STATUS_9765", "disabled"),
            "port": 9765,
        },
        "9766": {
            "status": env("BROWSER_STATUS_9766", "disabled"),
            "port": 9766,
        },
        "9767": {
            "status": env("BROWSER_STATUS_9767", "disabled"),
            "port": 9767,
        },
        "9768": {
            "status": env("BROWSER_STATUS_9768", "disabled"),
            "port": 9768,
        },
        "9769": {
            "status": env("BROWSER_STATUS_9769", "disabled"),
            "port": 9769,
        },
        "9770": {
            "status": env("BROWSER_STATUS_9770", "disabled"),
            "port": 9770,
        },
        "9771": {
            "status": env("BROWSER_STATUS_9771", "disabled"),
            "port": 9771,
        },
        "9772": {
            "status": env("BROWSER_STATUS_9772", "disabled"),
            "port": 9772,
        },
        "9773": {
            "status": env("BROWSER_STATUS_9773", "disabled"),
            "port": 9773,
        },
        "9774": {
            "status": env("BROWSER_STATUS_9774", "disabled"),
            "port": 9774,
        },
        "9775": {
            "status": env("BROWSER_STATUS_9775", "disabled"),
            "port": 9775,
        },
        "9776": {
            "status": env("BROWSER_STATUS_9776", "disabled"),
            "port": 9776,
        },
        "9777": {
            "status": env("BROWSER_STATUS_9777", "disabled"),
            "port": 9777,
        },
        "9778": {
            "status": env("BROWSER_STATUS_9778", "disabled"),
            "port": 9778,
        },
        "9779": {
            "status": env("BROWSER_STATUS_9779", "disabled"),
            "port": 9779,
        },
        "9780": {
            "status": env("BROWSER_STATUS_9780", "disabled"),
            "port": 9780,
        },
        "9781": {
            "status": env("BROWSER_STATUS_9781", "disabled"),
            "port": 9781,
        },
        "9782": {
            "status": env("BROWSER_STATUS_9782", "disabled"),
            "port": 9782,
        },
        "9783": {
            "status": env("BROWSER_STATUS_9783", "disabled"),
            "port": 9783,
        },
        "9784": {
            "status": env("BROWSER_STATUS_9784", "disabled"),
            "port": 9784,
        },
        "9785": {
            "status": env("BROWSER_STATUS_9785", "disabled"),
            "port": 9785,
        },
        "9786": {
            "status": env("BROWSER_STATUS_9786", "disabled"),
            "port": 9786,
        },
        "9787": {
            "status": env("BROWSER_STATUS_9787", "disabled"),
            "port": 9787,
        },
        "9788": {
            "status": env("BROWSER_STATUS_9788", "disabled"),
            "port": 9788,
        },
        "9789": {
            "status": env("BROWSER_STATUS_9789", "disabled"),
            "port": 9789,
        },
        "9790": {
            "status": env("BROWSER_STATUS_9790", "disabled"),
            "port": 9790,
        },
        "9791": {
            "status": env("BROWSER_STATUS_9791", "disabled"),
            "port": 9791,
        },
        "9792": {
            "status": env("BROWSER_STATUS_9792", "disabled"),
            "port": 9792,
        },
        "9793": {
            "status": env("BROWSER_STATUS_9793", "disabled"),
            "port": 9793,
        },
        "9794": {
            "status": env("BROWSER_STATUS_9794", "disabled"),
            "port": 9794,
        },

    }
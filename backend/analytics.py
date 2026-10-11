"""
analytics.py
------------------------------------------------
AI Crowd Risk Analytics Engine

Inputs
------
1. YOLO People Count
2. Piezo Sensor
3. IR Sensor
4. SW420 Sensor

Outputs
-------
• Crowd Risk Score
• Crowd Status
• Crowd Trend
• Alert Message

Author : Ved Rathod
"""

from collections import deque


class CrowdAnalytics:

    def __init__(self):

        # Store last 30 crowd counts
        self.history = deque(maxlen=30)

    # ----------------------------------------------------
    # Crowd Trend
    # ----------------------------------------------------

    def trend(self, people):

        self.history.append(people)

        if len(self.history) < 5:
            return "Stable"

        first = self.history[0]
        last = self.history[-1]

        if last > first + 2:
            return "Increasing"

        elif last < first - 2:
            return "Decreasing"

        return "Stable"

    # ----------------------------------------------------
    # Crowd Risk Score
    # ----------------------------------------------------

    def risk_score(self, people, piezo, ir, sw420):

        score = 0

        # ------------------------------------------------
        # 1. YOLO PEOPLE COUNT - 70%
        # ------------------------------------------------

        if people >= 30:
            score += 70

        elif people >= 20:
            score += 55

        elif people >= 10:
            score += 40

        elif people >= 5:
            score += 20

        # ------------------------------------------------
        # 2. SENSOR ACTIVITY - 30%
        # ------------------------------------------------
        # Piezo is currently the active physical sensor.
        # IR and SW420 are kept in the calculation so the
        # architecture is ready for additional sensors.
        # ------------------------------------------------

        sensor_score = 0

        # Piezo activity
        if piezo >= 500:
            sensor_score += 20

        elif piezo >= 300:
            sensor_score += 15

        elif piezo >= 150:
            sensor_score += 10

        elif piezo >= 80:
            sensor_score += 5

        # IR activity
        if ir > 0:
            sensor_score += 5

        # SW420 vibration activity
        if sw420 > 0:
            sensor_score += 5

        # Maximum sensor contribution = 30
        sensor_score = min(sensor_score, 30)

        score += sensor_score

        return min(score, 100)

    # ----------------------------------------------------
    # Crowd Status
    # ----------------------------------------------------

    def crowd_status(self, score):

        if score < 25:
            return "SAFE"

        elif score < 45:
            return "LOW"

        elif score < 70:
            return "MEDIUM"

        elif score < 90:
            return "HIGH"

        return "EMERGENCY"

    # ----------------------------------------------------
    # Alert Message
    # ----------------------------------------------------

    def alert(self, status):

        alerts = {

            "SAFE":
                "No Action Required",

            "LOW":
                "Crowd Under Control",

            "MEDIUM":
                "Monitor Crowd",

            "HIGH":
                "Security Attention Required",

            "EMERGENCY":
                "Immediate Action Required"
        }

        return alerts[status]

    # ----------------------------------------------------
    # Main Analysis Function
    # ----------------------------------------------------

    def analyze(self, people, piezo=0, ir=0, sw420=0):

        score = self.risk_score(
            people,
            piezo,
            ir,
            sw420
        )

        status = self.crowd_status(score)

        trend = self.trend(people)

        return {
            "verified_count": people,
            "people": people,
            "piezo": piezo,
            "ir": ir,
            "sw420": sw420,
            "risk_score": score,
            "status": status,
            "trend": trend,
            "alert": self.alert(status)
        }
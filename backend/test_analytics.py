from analytics import CrowdAnalytics

analytics = CrowdAnalytics()

while True:

    people = int(input("People : "))
    piezo = int(input("Piezo : "))
    ir = int(input("IR (0/1): "))
    sw = int(input("SW420 (0/1): "))

    result = analytics.analyze(
        people,
        piezo,
        ir,
        sw
    )

    print()

    print(result)

    print("--------------------------------")
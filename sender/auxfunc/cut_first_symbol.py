def do(minute):
    if minute[:1] == '0':
        return minute[1:]
    else:
        return minute

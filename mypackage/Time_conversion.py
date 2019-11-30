def time (tempo, day, hour, minutes, seconds):
        day = tempo//86400
        hour = tempo%86400//3600
        minutes = ((tempo%86400)%3600)//60
        seconds = (((tempo%86400)%3600)%60)
        return(day,hour,minutes,seconds)

package com.sophvlight.auth_service.Standards;

import java.time.LocalDateTime;
import java.util.Date;

public class Time {
    public static LocalDateTime now(){
        return LocalDateTime.now();
    }
    public static Date afterNow(long millis){
        return new Date(System.currentTimeMillis()+millis);
    }
}


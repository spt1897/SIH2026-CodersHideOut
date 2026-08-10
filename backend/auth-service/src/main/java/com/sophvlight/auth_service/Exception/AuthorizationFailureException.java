package com.sophvlight.auth_service.Exception;

public class AuthorizationFailureException extends Exception {
    public AuthorizationFailureException(String msg){
        super(msg);
    }
}

package com.sophvlight.auth_service.Exception;

import java.util.HashMap;
import java.util.Map;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

import com.sophvlight.auth_service.Standards.Time;

@RestControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {
    @ExceptionHandler(value=AuthorizationFailureException.class)
    public ResponseEntity<?> handleException(AuthorizationFailureException e){
        return new ResponseEntity<>(e.getMessage(),HttpStatus.UNAUTHORIZED);
    }
    @ExceptionHandler(value=GeneralException.class)
    public ResponseEntity<?> handleGeneralException(GeneralException e){
        String s[] = e.getMessage().split(":");
        int code = Integer.parseInt(s[0]);
        String msg = s[1];
        Map<String,Object> map = new HashMap<>();
        map.put("timestamp",Time.now());
        map.put("status", code);
        map.put("message", msg);
        return new ResponseEntity<>(map,HttpStatus.valueOf(code));
    }
    @Override
protected ResponseEntity<Object> handleMethodArgumentNotValid(
    MethodArgumentNotValidException ex, HttpHeaders headers, HttpStatusCode status, WebRequest request) {
    
    Map<String, String> errors = new HashMap<>();
    // Extract detailed error information
    ex.getBindingResult().getFieldErrors().forEach(error -> {
        errors.put(error.getField(), error.getDefaultMessage());
    });

    // Create a structured response object
    Map<String, Object> responseBody = new HashMap<>();
    responseBody.put("timestamp", Time.now());
    responseBody.put("status", status.value());
    responseBody.put("error", "Bad Request");
    responseBody.put("message", "Validation failed for request arguments");
    responseBody.put("details", errors); // Include detailed field errors
    
    return new ResponseEntity<>(responseBody, HttpStatus.BAD_REQUEST);
}

}

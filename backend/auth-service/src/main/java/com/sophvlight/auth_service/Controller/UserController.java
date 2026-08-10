package com.sophvlight.auth_service.Controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.sophvlight.auth_service.DTO.TokenDTO;
import com.sophvlight.auth_service.DTO.UserDTO;
import com.sophvlight.auth_service.Exception.AuthorizationFailureException;
import com.sophvlight.auth_service.Exception.GeneralException;
import com.sophvlight.auth_service.Model.UserData;
import com.sophvlight.auth_service.Model.Users;
import com.sophvlight.auth_service.Service.UserService;


@RestController
@RequestMapping("/user")
public class UserController {
    private UserService service;
    @Autowired
    public UserController(UserService service){
        this.service=service;
    }
    @GetMapping("/secure-test")
    public ResponseEntity<String> testSecureRoute(@RequestHeader(value = "X-Auth-Username", required = false) String username) {
        if (username == null) {
            return ResponseEntity.badRequest().body("Gateway failed to inject username header!");
        }
        return ResponseEntity.ok("Success! The API Gateway validated the token for user: " + username);
    }
    @PostMapping("/register")
    public ResponseEntity<TokenDTO> registerUser(@AuthenticationPrincipal UserData details, @RequestBody Users user) throws GeneralException{
        return new ResponseEntity<>(service.register(user));
    }
    @PostMapping("/login")
    public ResponseEntity<TokenDTO> loginUser(@RequestBody UserDTO user) throws AuthorizationFailureException{
        return new ResponseEntity<>(service.login(user),HttpStatus.OK);
    }
    @PostMapping("/refresh")
    public ResponseEntity<TokenDTO> refreshUser(@RequestHeader(value = "refresh-token",required = false) String refreshToken) throws AuthorizationFailureException{
        return new ResponseEntity<>(service.refresh(refreshToken),HttpStatus.OK);
    }
    @PostMapping("/logout")
    public ResponseEntity<TokenDTO> logoutUser(@AuthenticationPrincipal UserDetails uds) throws AuthorizationFailureException{
        service.endSession(uds);
        return new ResponseEntity<>(HttpStatus.OK);
    }
}

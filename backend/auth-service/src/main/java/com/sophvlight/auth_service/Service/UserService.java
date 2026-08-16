package com.sophvlight.auth_service.Service;

import java.util.Set;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import com.google.api.client.googleapis.auth.oauth2.GoogleIdToken;
import com.sophvlight.auth_service.DTO.TokenDTO;
import com.sophvlight.auth_service.DTO.UserDTO;
import com.sophvlight.auth_service.Exception.AuthorizationFailureException;
import com.sophvlight.auth_service.Exception.GeneralException;
import com.sophvlight.auth_service.Model.RefreshToken;
import com.sophvlight.auth_service.Model.UserData;
import com.sophvlight.auth_service.Model.Users;
import com.sophvlight.auth_service.Repo.RefreshTokenRepo;
import com.sophvlight.auth_service.Repo.UserRepo;
import com.sophvlight.auth_service.Standards.Role;
import com.sophvlight.auth_service.Standards.Time;

@Service
public class UserService implements UserDetailsService {
    private final UserRepo db;
    private final RefreshTokenService rtService;
    private final RefreshTokenRepo db2;
    private final JWTService jwtService;
    private final ApplicationContext context;
    private GoogleOAuthService oAuth;

    @Autowired
    public UserService(UserRepo db,
            RefreshTokenService rtService,
            RefreshTokenRepo db2,
            JWTService jwtService,
            ApplicationContext context,
            GoogleOAuthService oAuth) {
        this.db = db;
        this.rtService = rtService;
        this.db2 = db2;
        this.jwtService = jwtService;
        this.context = context;
        this.oAuth=oAuth;
    }

    public HttpStatus register(Users user) throws GeneralException {
        if (db.findByEmail(user.getEmail()) != null)
            throw new GeneralException("409:Email already exists");
        BCryptPasswordEncoder encoder = context.getBean(BCryptPasswordEncoder.class);
        user.setPassword(encoder.encode(user.getPassword()));
        user.setCreatedAt(Time.now());
        user.setLastLogin(Time.now());
        db.save(user);
        return HttpStatus.CREATED;
    }

    public TokenDTO login(UserDTO dto) throws AuthorizationFailureException {
        AuthenticationManager manager = context.getBean(AuthenticationManager.class);
        Authentication auth = manager
                .authenticate(new UsernamePasswordAuthenticationToken(dto.email(), dto.password()));
        if (!auth.isAuthenticated())
            throw new AuthorizationFailureException("Incorrect email or password");
        Users user = db.findByEmail(dto.email());
        user.setLastLogin(Time.now());
        db.save(user);
        return generateToken(user.getEmail(), user.getId(),user.getRole());
    }

    private TokenDTO generateToken(String username, int id,String role) {
        String accessToken = jwtService.generateToken(username,id,role);
        String refreshToken = rtService.generateToken(username);
        db2.save(new RefreshToken(id, refreshToken));
        return new TokenDTO(accessToken, refreshToken,role);
    }

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        Users user = db.findByEmail(email);
        if (user == null)
            throw new UsernameNotFoundException("Email No registered");
        return new UserData(user);
    }

    public TokenDTO refresh(String refreshToken) throws AuthorizationFailureException {
        RefreshToken token = db2.findByToken(refreshToken);
        if (token == null || rtService.isTokenExpired(refreshToken))
            throw new AuthorizationFailureException("Invalid Token");
        Users user = db.findById(token.getUserId()).get();
        if (user == null || !user.getEmail().equals(rtService.extractUserName(refreshToken)))
            throw new AuthorizationFailureException("Invalid User");
        return generateToken(user.getEmail(), user.getId(),user.getRole());
    }

    public void endSession(UserDetails usd) throws AuthorizationFailureException {
        Users user = db.findByEmail(usd.getUsername());
        if (user == null)
            throw new AuthorizationFailureException("Invalid User");
        db2.deleteById(user.getId());
    }

    public int getUserIdByUsername(String username) throws GeneralException {
        Users user = db.findByUsername(username);
        if (user == null)
            throw new GeneralException("400:User not found");
        return user.getId();
    }
    public Set<Integer> getUserIdsByUsernames(Set<String> usernames) throws GeneralException {
        Set<Integer> ids = db.fetchAllIdsByUsernames(usernames);
        if (ids.isEmpty())
            throw new GeneralException("400:Users not found");
        return ids;
    }
    public String getUsernameByUserId(int userId) throws GeneralException {
        Users user = db.getReferenceById(userId);
        if (user == null)
            throw new GeneralException("400:User not found");
        return user.getUsername();
    }
    public Set<String> getUsernameByUserId(Set<Integer> ids) throws GeneralException {
        Set<String> usernames = db.fetchAllUsernamesByIds(ids);
        if (usernames.isEmpty())
            throw new GeneralException("404:No Participants");
        return usernames;
    }

    public TokenDTO oauth(String googleToken) throws AuthorizationFailureException{
        try {

            GoogleIdToken.Payload payload = oAuth.verifyToken(googleToken);
            String email = payload.getEmail();
            
            Users user = db.findByEmail(email);
            
            if (user == null) {
                user = new Users();
                user.setEmail(email);
                user.setUsername((String) payload.get("name"));
                user.setRole(Role.USER);
                user.setPassword(UUID.randomUUID().toString()); 
                user.setCreatedAt(Time.now());
                user.setLastLogin(Time.now());
                user = db.save(user);
            }

            TokenDTO tokenDTO = generateToken(user.getEmail(), user.getId(), user.getRole());
            
            return tokenDTO;

        } catch (Exception e) {
            System.err.println("CRITICAL OAUTH ERROR: " + e.getMessage());
            e.printStackTrace();
            throw new AuthorizationFailureException("You are not a valid google user");
        }
    }
}

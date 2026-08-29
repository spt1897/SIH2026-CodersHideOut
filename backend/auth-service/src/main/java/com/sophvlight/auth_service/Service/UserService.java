package com.sophvlight.auth_service.Service;

import java.util.List;
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
import com.sophvlight.auth_service.DTO.PublicRegisterDTO;
import com.sophvlight.auth_service.DTO.RegisterDTO;
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

    public HttpStatus publicRegister(PublicRegisterDTO dto) throws GeneralException {
        // 1. Generate Synthetic Email to satisfy DB and Spring Security constraints
        String syntheticEmail = dto.phno() + "@citizen.in";

        if (db.findByEmail(syntheticEmail) != null) {
            throw new GeneralException("409:Mobile number already registered");
        }

        BCryptPasswordEncoder encoder = context.getBean(BCryptPasswordEncoder.class);

        // 2. Map DTO to Entity
        Users user = new Users();
        user.setEmail(syntheticEmail); 
        user.setPhno(dto.phno());
        user.setPassword(encoder.encode(dto.password()));
        
        // Handle optional name
        user.setName((dto.name() != null && !dto.name().isBlank()) ? dto.name() : "Citizen");
        
        user.setRole(Role.USER); // Default Citizen Role
        
        // Map Location and Language
        user.setH3Res6Cells(dto.homeLocation()); 
        user.setPreferredLanguage(dto.preferredLanguage());
        
        // Defaults for unused official fields
        user.setAgency("PUBLIC");
        user.setStateCode("N/A");
        user.setDistrictCodes("");
        user.setDesignation("Citizen");
        user.setEmployeeId("CITIZEN_" + dto.phno());

        user.setCreatedAt(Time.now());
        user.setLastLogin(Time.now());
        
        db.save(user);

        return HttpStatus.CREATED;
    }

    public HttpStatus adminRegister(RegisterDTO dto) throws GeneralException {
        if (db.findByEmail(dto.email()) != null)
            throw new GeneralException("409:Email already exists");
            
        BCryptPasswordEncoder encoder = context.getBean(BCryptPasswordEncoder.class);
        
        // Flatten the DTO arrays into comma-separated strings for DB storage
        String districtCodesStr = String.join(",", dto.jurisdiction().districtCodes());
        String h3CellsStr = String.join(",", dto.jurisdiction().h3Res6Cells());

        // Map DTO to the updated Users Entity
        Users user = new Users(
            dto.email(),
            dto.phno(),
            encoder.encode(dto.password()),
            dto.role(),
            dto.name(),
            dto.designation(),
            dto.employeeId(),
            dto.agency(),
            dto.jurisdiction().stateCode(),
            districtCodesStr,
            h3CellsStr
        );
        
        user.setCreatedAt(Time.now());
        user.setLastLogin(Time.now());
        db.save(user);
        
        // Removed: sendDataToUserProfileService() - No longer required in Fat Token architecture
        return HttpStatus.CREATED;
    }

    public TokenDTO login(UserDTO dto) throws AuthorizationFailureException {
        String identifier = dto.identifier();// This now holds either an email or a phone number
        
        AuthenticationManager manager = context.getBean(AuthenticationManager.class);
        
        // This will trigger our updated loadUserByUsername internally
        Authentication auth = manager
                .authenticate(new UsernamePasswordAuthenticationToken(identifier, dto.password()));
                
        if (!auth.isAuthenticated())
            throw new AuthorizationFailureException("Incorrect credentials");
            
        // Retrieve the user to update the login timestamp and generate the token
        Users user;
        if (identifier.matches("^[0-9]{10}$")) {
            user = db.findByPhno(identifier);
        } else {
            user = db.findByEmail(identifier);
        }
        
        user.setLastLogin(Time.now());
        db.save(user);
        
        return generateToken(user);
    }

    // Updated to handle the Fat Token requirement using the Users entity
    private TokenDTO generateToken(Users user) {
        // Generating a unique subject ID
        String subjectId = "user_usr_" + user.getId();
        
        
        List<String> permissions = List.of("alerts:issue", "simulation:view_detailed"); 
        
        // We pass the full Users entity to JWTService now
        String accessToken = jwtService.generateToken(subjectId, user, permissions);
        String refreshToken = rtService.generateToken(user.getEmail());
        
        db2.save(new RefreshToken(user.getId(), refreshToken));
        return new TokenDTO(accessToken, refreshToken, user.getRole());
    }

    @Override
    public UserDetails loadUserByUsername(String identifier) throws UsernameNotFoundException {
        Users user;
        
        // If the identifier is exactly 10 digits, treat it as a phone number
        if (identifier.matches("^[0-9]{10}$")) {
            user = db.findByPhno(identifier);
        } else {
            user = db.findByEmail(identifier);
        }
        
        if (user == null) {
            throw new UsernameNotFoundException("User not registered");
        }
        
        return new UserData(user);
    }

    public TokenDTO refresh(String refreshToken) throws AuthorizationFailureException {
        RefreshToken token = db2.findByToken(refreshToken);
        if (token == null || rtService.isTokenExpired(refreshToken))
            throw new AuthorizationFailureException("Invalid Token");
            
        Users user = db.findById(token.getUserId()).get();
        if (user == null || !user.getEmail().equals(rtService.extractUserName(refreshToken)))
            throw new AuthorizationFailureException("Invalid User");
            
        return generateToken(user);
    }

    public void endSession(UserDetails usd) throws AuthorizationFailureException {
        Users user = db.findByEmail(usd.getUsername());
        if (user == null)
            throw new AuthorizationFailureException("Invalid User");
        db2.deleteById(user.getId());
    }

    // ... keeping your other existing username/ID lookup methods exactly as they were ...

    public TokenDTO oauth(String googleToken) throws AuthorizationFailureException{
        try {
            GoogleIdToken.Payload payload = oAuth.verifyToken(googleToken);
            String email = payload.getEmail();
            
            Users user = db.findByEmail(email);
            
            if (user == null) {
                user = new Users();
                user.setEmail(email);
                // Note: user.setUsername is not in the new Users entity, mapping to Name instead
                user.setName((String) payload.get("name")); 
                user.setRole(Role.USER);
                user.setPassword(UUID.randomUUID().toString()); 
                user.setCreatedAt(Time.now());
                user.setLastLogin(Time.now());
                
                // Set empty defaults for jurisdiction to prevent null pointers in JWT generation
                user.setAgency("N/A");
                user.setStateCode("N/A");
                user.setDistrictCodes("");
                user.setH3Res6Cells("");
                
                user = db.save(user);
            }

            return generateToken(user);

        } catch (Exception e) {
            System.err.println("CRITICAL OAUTH ERROR: " + e.getMessage());
            e.printStackTrace();
            throw new AuthorizationFailureException("You are not a valid google user");
        }
    }
}
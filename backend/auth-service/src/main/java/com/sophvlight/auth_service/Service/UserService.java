package com.sophvlight.auth_service.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationContext;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

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
    private final GoogleOAuthService oAuth;
    private final RestTemplate restTemplate;

    @Value("${services.user-service.url:http://user-service}")
    private String userServiceBaseUrl;

    @Autowired
    public UserService(UserRepo db,
            RefreshTokenService rtService,
            RefreshTokenRepo db2,
            JWTService jwtService,
            ApplicationContext context,
            GoogleOAuthService oAuth,
            RestTemplate restTemplate) {
        this.db = db;
        this.rtService = rtService;
        this.db2 = db2;
        this.jwtService = jwtService;
        this.context = context;
        this.oAuth = oAuth;
        this.restTemplate = restTemplate;
    }

    public HttpStatus publicRegister(PublicRegisterDTO dto) throws GeneralException {
        String syntheticEmail = dto.phno() + "@citizen.in";

        if (db.findByEmail(syntheticEmail) != null) {
            throw new GeneralException("409:Mobile number already registered");
        }

        BCryptPasswordEncoder encoder = context.getBean(BCryptPasswordEncoder.class);
        String encodedPassword = encoder.encode(dto.password());

        Users user = new Users();
        user.setEmail(syntheticEmail); 
        user.setPhno(dto.phno());
        user.setPassword(encodedPassword);
        user.setName((dto.name() != null && !dto.name().isBlank()) ? dto.name() : "Citizen");
        user.setRole(Role.USER); 
        user.setH3Res6Cells(dto.homeLocation()); 
        user.setPreferredLanguage(dto.preferredLanguage());
        user.setAgency("PUBLIC");
        user.setStateCode("N/A");
        user.setDistrictCodes("");
        user.setDesignation("Citizen");
        user.setEmployeeId("CITIZEN_" + dto.phno());
        user.setCreatedAt(Time.now());
        user.setLastLogin(Time.now());
        
        db.save(user);

        // Fire the sync payload to FastAPI
        syncCitizenToUserService(dto, encodedPassword, syntheticEmail);

        return HttpStatus.CREATED;
    }

    public HttpStatus adminRegister(RegisterDTO dto) throws GeneralException {
        if (db.findByEmail(dto.email()) != null)
            throw new GeneralException("409:Email already exists");
            
        BCryptPasswordEncoder encoder = context.getBean(BCryptPasswordEncoder.class);
        String encodedPassword = encoder.encode(dto.password());
        
        String districtCodesStr = String.join(",", dto.jurisdiction().districtCodes());
        String h3CellsStr = String.join(",", dto.jurisdiction().h3Res6Cells());

        Users user = new Users(
            dto.email(),
            dto.phno(),
            encodedPassword,
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
        
        // Fire the sync payload to FastAPI
        syncAdminToUserService(dto, encodedPassword, districtCodesStr, h3CellsStr);

        return HttpStatus.CREATED;
    }

    private void syncAdminToUserService(RegisterDTO dto, String encodedPassword, String districtCodesStr, String h3CellsStr) {
        try {
            String url = userServiceBaseUrl + "/api/v1/sync/admin";

            Map<String, Object> payload = new HashMap<>();
            payload.put("name", dto.name());
            payload.put("email", dto.email());
            payload.put("phno", dto.phno());
            payload.put("password", encodedPassword);
            payload.put("role", dto.role());
            payload.put("designation", dto.designation());
            payload.put("employee_id", dto.employeeId());
            payload.put("agency", dto.agency());
            payload.put("state_code", dto.jurisdiction().stateCode());
            payload.put("district_codes", districtCodesStr);
            payload.put("h3_res6_cells", h3CellsStr);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(payload, headers);

            restTemplate.postForEntity(url, request, String.class);
            System.out.println("[SYNC SUCCESS] Admin dispatched to User Service");
        } catch (Exception e) {
            System.err.println("[SYNC ERROR] Failed to dispatch admin to UserService: " + e.getMessage());
        }
    }

    private void syncCitizenToUserService(PublicRegisterDTO dto, String encodedPassword, String email) {
        try {
            String url = userServiceBaseUrl + "/api/v1/sync/citizen";

            Map<String, Object> payload = new HashMap<>();
            payload.put("name", (dto.name() != null && !dto.name().isBlank()) ? dto.name() : "Citizen");
            payload.put("phno", dto.phno());
            payload.put("email", email);
            payload.put("password", encodedPassword);
            payload.put("role", Role.USER);
            payload.put("h3_home_cell", dto.homeLocation());
            payload.put("preferred_language", dto.preferredLanguage());

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(payload, headers);

            restTemplate.postForEntity(url, request, String.class);
            System.out.println("[SYNC SUCCESS] Citizen dispatched to User Service");
        } catch (Exception e) {
            System.err.println("[SYNC ERROR] Failed to dispatch citizen to UserService: " + e.getMessage());
        }
    }

    public TokenDTO login(UserDTO dto) throws AuthorizationFailureException {
        String identifier = dto.identifier();
        
        AuthenticationManager manager = context.getBean(AuthenticationManager.class);
        Authentication auth = manager
                .authenticate(new UsernamePasswordAuthenticationToken(identifier, dto.password()));
                
        if (!auth.isAuthenticated())
            throw new AuthorizationFailureException("Incorrect credentials");
            
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

    private TokenDTO generateToken(Users user) {
        String subjectId = "user_usr_" + user.getId();
        List<String> permissions = List.of("alerts:issue", "simulation:view_detailed"); 
        
        String accessToken = jwtService.generateToken(subjectId, user, permissions);
        String refreshToken = rtService.generateToken(user.getEmail());
        
        db2.save(new RefreshToken(user.getId(), refreshToken));
        return new TokenDTO(accessToken, refreshToken, user.getRole());
    }

    @Override
    public UserDetails loadUserByUsername(String identifier) throws UsernameNotFoundException {
        Users user;
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

    public TokenDTO oauth(String googleToken) throws AuthorizationFailureException{
        try {
            GoogleIdToken.Payload payload = oAuth.verifyToken(googleToken);
            String email = payload.getEmail();
            
            Users user = db.findByEmail(email);
            
            if (user == null) {
                user = new Users();
                user.setEmail(email);
                user.setName((String) payload.get("name")); 
                user.setRole(Role.USER);
                user.setPassword(UUID.randomUUID().toString()); 
                user.setCreatedAt(Time.now());
                user.setLastLogin(Time.now());
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
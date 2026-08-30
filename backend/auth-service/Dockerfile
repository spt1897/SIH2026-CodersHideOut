FROM eclipse-temurin:21-jdk-alpine
VOLUME /tmp
ADD target/*.jar auth-service.jar
ENTRYPOINT ["java", "-jar", "/auth-service.jar"]
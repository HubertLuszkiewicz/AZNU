FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
RUN mkdir -p src/main/java
COPY *.java src/main/java/
RUN mvn clean package
RUN echo "=== Files in target ===" && ls -la /app/target/
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/compliance-service-shaded.jar app.jar
CMD ["java", "-jar", "app.jar"]
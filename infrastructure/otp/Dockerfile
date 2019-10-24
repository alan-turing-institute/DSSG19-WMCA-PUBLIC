FROM java:8

ARG gtfs_app_id
ARG gtfs_app_key

# Create directory which will contain OTP .jar file
# Create directory which will contain OTP inputs
RUN mkdir -p /otp /otp-inputs

# Must be inside /otp directory to launch server later
WORKDIR /otp

# GTFS data
#ADD http://api.tfwm.org.uk/gtfs/tfwm_gtfs.zip?app_id=${gtfs_app_id}&app_key=${gtfs_app_key} /otp-inputs

ADD ./data/tfwm_gtfs_augmented.zip /otp-inputs

# Get the OTP jar file
ADD https://repo1.maven.org/maven2/org/opentripplanner/otp/1.3.0/otp-1.3.0-shaded.jar /otp

# OSM data
ADD http://download.geofabrik.de/europe/great-britain/england/west-midlands-latest.osm.pbf /otp-inputs

# Server
ENTRYPOINT ["java", "-Xmx16G", "-jar", "/otp/otp-1.3.0-shaded.jar", "--build", "/otp-inputs", "--inMemory"]

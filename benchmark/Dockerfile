# Idle IBM MAS-Manage-UI JMeter runner (UBI + OpenJDK).
# Main process sleeps; start a run with: oc exec deploy/mas-bench -- /opt/benchmark/run.sh 86400
FROM registry.access.redhat.com/ubi9/ubi-minimal:latest

ENV JMETER_VERSION=5.6.3 \
    JMETER_HOME=/opt/apache-jmeter \
    PATH=/opt/apache-jmeter/bin:/usr/bin:$PATH \
    HOME=/tmp \
    LANG=C.UTF-8

RUN microdnf install -y --nodocs \
        java-17-openjdk-headless tar gzip findutils shadow-utils python3 \
    && microdnf clean all \
    && curl -fsSL "https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz" \
        | tar -xz -C /opt \
    && mv "/opt/apache-jmeter-${JMETER_VERSION}" "${JMETER_HOME}" \
    && mkdir -p /opt/benchmark \
    && printf 'app:x:1001:0:app:/tmp:/sbin/nologin\n' >> /etc/passwd \
    && chown -R 1001:0 /opt/apache-jmeter /opt/benchmark \
    && chmod -R g+rwX /opt/apache-jmeter /opt/benchmark

COPY MAS-Manage-UI.jmx summarize_jtl.py run.sh /opt/benchmark/
RUN chmod 0755 /opt/benchmark/run.sh \
    && chown -R 1001:0 /opt/benchmark

USER 1001
WORKDIR /opt/benchmark
# Idle until someone execs run.sh (keep the 24h JMeter process off the laptop).
CMD ["sleep", "infinity"]

Name:		checker-qual
Version:	4.4.0
Release:	1
Summary:	Checker Framework type qualifiers
Group:		Development/Java
License:	MIT
URL:		https://checkerframework.org/
Source0:	https://github.com/typetools/checker-framework/archive/refs/tags/checker-framework-%{version}.tar.gz#/checker-qual-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar

%description
checker-qual %{version} contains the type qualifiers recognized by the
Checker Framework. Auto Common annotates its API with @Nullable from
this jar.

%prep
%autosetup -n checker-framework-checker-framework-%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
find checker-qual/src/main/java -name '*.java' ! -name 'module-info.java' > sources.list
test "$(wc -l < sources.list)" -eq 395
mkdir -p classes
javac --release 8 -encoding UTF-8 -d classes @sources.list
jar cf checker-qual.jar -C classes .
jar tf checker-qual.jar | grep -E '\.(java|jar|so|node|wasm)$' && exit 1 || true
javap -verbose -cp checker-qual.jar org.checkerframework.checker.nullness.qual.Nullable | grep -F 'major version: 52'

cat > checker-qual.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.checkerframework</groupId>
  <artifactId>checker-qual</artifactId>
  <version>4.4.0</version>
  <name>Checker Qual</name>
  <description>Checker Framework type qualifiers</description>
  <licenses>
    <license>
      <name>MIT</name>
    </license>
  </licenses>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact checker-qual.pom:checker-qual.jar \
	--file-name checker-qual \
	--filelist .mfiles

%check
mkdir -p check
cat > check/Smoke.java << 'END'
import org.checkerframework.checker.nullness.qual.Nullable;
public class Smoke {
	public @Nullable String value;
	public static void main(String[] args) throws Exception {
		java.lang.reflect.AnnotatedType t = Smoke.class.getField("value").getAnnotatedType();
		Nullable marker = t.getAnnotation(Nullable.class);
		if (marker == null) {
			throw new RuntimeException("missing Nullable");
		}
		System.out.println("checker_qual_ok " + marker.annotationType().getSimpleName());
	}
}
END
JAR=%{buildroot}%{_javadir}/checker-qual.jar
test -f "$JAR"
javac --release 8 -encoding UTF-8 -cp "$JAR" -d check check/Smoke.java
java -cp "check:$JAR" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'checker_qual_ok Nullable' check/out.txt

%files -f .mfiles
%doc checker-qual/LICENSE.txt

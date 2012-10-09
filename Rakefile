PROJ = "letter"
VERS = File.read("letter/_version.py").scan(/__version__ = ['"]([^'"]*)/)[0][0]

# RPM build CONSTANTS
SOURCED="build/rpm/SOURCES/"

task :test do
  p "Running unit tests for #{PROJ}"
  sh "python -m pytest test"
end

task :rpm do
  p "Building RPM for #{PROJ}"
  %x[cd adb &&  python setup.py sdist]
  sh "rm -rf build"
  sh "rm -rf MANIFEST"
  %w[BUILD SOURCES SPECS RPMS SRPMS].each do |d|
    %x[mkdir -p build/rpm/#{d}]
  end

  sh "cp letter/dist/*.tar.gz #{SOURCED}"
  sh "cp packaging/#{PROJ}.template.spec build/rpm/SPECS/#{PROJ}.spec"
  sh "cp requirements.txt #{SOURCED}"

  %x[echo "%_topdir `pwd`/build/rpm" > ~/.rpmmacros]

  %w[BUILD VERS].each do |v|
    sh "perl -pi -e 's/#{v}_NUMBER/#{eval v}/' build/rpm/SPECS/#{PROJ}.spec"
  end

  sh "rpmbuild -ba build/rpm/SPECS/#{PROJ}.spec"

end

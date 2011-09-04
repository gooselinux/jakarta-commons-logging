# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _without_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define base_name  logging
%define short_name commons-%{base_name}
%define section    free

Name:           jakarta-%{short_name}
Version:        1.0.4
Release:        10%{?dist}
Epoch:          0
Summary:        Jakarta Commons Logging Package
License:        ASL 2.0
Group:          Development/Libraries
URL:            http://jakarta.apache.org/commons/%{base_name}/
#wget http://www.apache.org/dist/jakarta/commons/logging/source/commons-logging-1.0.4-src.tar.gz
Source0:        commons-logging-1.0.4-src.tar.gz
Patch0:         commons-logging-1.0.4-build_xml.patch
Patch1:         %{short_name}-eclipse-manifest.patch
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  ant >= 0:1.6
BuildRequires:  junit
BuildRequires:  avalon-logkit
BuildRequires:  avalon-framework
BuildRequires:  log4j
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
Requires(post):   java-gcj-compat
Requires(postun): java-gcj-compat
%endif

%description
The commons-logging package provides a simple, component oriented
interface (org.apache.commons.logging.Log) together with wrappers for
logging systems. The user can choose at runtime which system they want
to use. In addition, a small number of basic implementations are
provided to allow users to use the package standalone. 
commons-logging was heavily influenced by Avalon's Logkit and Log4J. The
commons-logging abstraction is meant to minimize the differences between
the two, and to allow a developer to not tie himself to a particular
logging implementation.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Documentation
# for /bin/rm and /bin/ln
Requires(post):   coreutils
Requires(postun): coreutils

%description    javadoc
Javadoc for %{name}.

# -----------------------------------------------------------------------------

%prep
%setup -q -n %{short_name}-%{version}-src
%patch0 -b .sav
pushd src/conf
%patch1 -p1
popd

# -----------------------------------------------------------------------------

%build
cat > build.properties <<EOBM
junit.jar=$(build-classpath junit)
log4j.jar=$(build-classpath log4j)
log4j12.jar=$(build-classpath log4j)
logkit.jar=$(build-classpath avalon-logkit)
avalon-framework-api.jar=$(build-classpath avalon-framework)
avalon-framework-impl.jar=$(build-classpath avalon-framework)
EOBM

ant compile.tests dist

# FIXME: There are failures with gcj. Ignore them for now.
%if %{gcj_support}
  ant -Dtest.failonerror=false test
%else
  ant test
%endif

# -----------------------------------------------------------------------------

%install
rm -rf $RPM_BUILD_ROOT

# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -p -m 644 dist/%{short_name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
install -p -m 644 dist/%{short_name}-api.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-api-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed "s|jakarta-||g"`; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# -----------------------------------------------------------------------------

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

# -----------------------------------------------------------------------------

%post
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%postun
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%files
%defattr(0644,root,root,0755)
%doc PROPOSAL.html STATUS.html LICENSE.txt RELEASE-NOTES.txt
%{_javadir}/*

%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

# -----------------------------------------------------------------------------

%changelog
* Tue Feb 02 2010 Jeff Johnston <jjohnstn@redhat.com> - 0:1.0.4-10
- Remove post and postun steps for javadoc subpackage
- Default to noarch
- Fix rpmlint warnings

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0:1.0.4-9.9
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.0.4-9.8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.0.4-8.8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jul 11 2008 Andrew Overholt <overholt@redhat.com> 0:1.0.4-7.7
- Update OSGi bundle version.

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.0.4-7.7
- drop repotag

* Thu May 29 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.0.4-7jpp.6
- fix license tag

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:1.0.4-7jpp.5
- Autorebuild for GCC 4.3

* Tue Nov  6 2007 Stepan Kasal <skasal@redhat.com> - 1.0.4-6jpp.5
- fix typo in description

* Thu Sep 20 2007 Deepak Bhole <dbhole@redhat.com> 0:1.0.4-6jpp.4
- Add %%{?dist} to release as per policy

* Wed Aug 29 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 1.0.4-6jpp.3
- Rebuild for selinux ppc32 issue.

* Wed Jul 11 2007 Ben Konrath <bkonrath@redhat.com> - 0:1.0.4-6jpp.2
- Add eclipse-manifest patch.

* Thu Aug 10 2006 Deepak Bhole <dbhole@redhat.com> 0:1.0.4-6jpp.1
- Added missing requirements.

* Thu Aug 10 2006 Karsten Hopp <karsten@redhat.de> 0:1.0.4-5jpp_3fc
- Require(post/postun): coreutils

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> 0:1.0.4-5jpp_2fc
- Rebuilt

* Wed Jul 19 2006 Deepak Bhole <dbhole@redhat.com> 0:1.0.4-5jpp_1fc
- Remove name/release/version defines as applicable.

* Mon Jul 17 2006 Deepak Bhole <dbhole@redhat.com> 0:1.0.4-4jpp
- Added conditional native compiling.

* Thu Mar 30 2006 Ralph Apel <r.apel at r-apel.de> - 0:1.0.4-3jpp
- Replace avalon-logkit with new excalibur-avalon-logkit

* Sun Aug 23 2004 Randy Watler <rwatler at finali.com> - 0:1.0.4-2jpp
- Rebuild with ant-1.6.2

* Thu Jun 24 2004 Kaj J. Niemi <kajtzu@fi.basen.net> - 0:1.0.4-1jpp
- Update to 1.0.4 (tomcat 5.0.27 wants it)
- Drop Patch #0 (jakarta-commons-logging-noclasspath.patch), unnecessary
 
* Tue Jun 17 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.0.3-4jpp
- Drop log4j requirement and manifest Class-Path.
- Run unit tests during build.
- Nuke spurious subdir in -javadoc package.
- Some spec file cleanups.

* Fri May 09 2003 David Walluck <david@anti-microsoft.org> 0:1.0.3-3jpp
- update for JPackage 1.5

* Fri Mar 11 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.0.3-2jpp
- update spec to respect JPP 1.5 policy

* Wed Mar 09 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.0.3-1jpp
- 1.0.3
- Built with IBM SDK 1.4 to have JDK 1.4 support compiled in

* Thu Feb 27 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.0.2-2jpp
- fix ASF license and add packager tag

* Mon Sep 30 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0.2-1jpp
- 1.0.2

* Tue Aug 20 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0.1-1jpp
- 1.0.1

* Fri Jul 12 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-5jpp
- remove Requires logkit (commons-log could works with log4j, jdk1.4)

* Mon Jun 10 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-4jpp
- use sed instead of bash 2.x extension in link area to make spec compatible
  with distro using bash 1.1x

* Mon Jun 10 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-3jpp
- built with Sun JDK 1.4.0_01 to have JDK 1.4 support compiled in

* Fri Jun 07 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-2jpp
- added short names in %%{javadir}, as does jakarta developpers 

* Mon May 06 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.0-1jpp 
- fist jpp release

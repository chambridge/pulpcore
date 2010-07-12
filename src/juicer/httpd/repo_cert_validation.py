#!/usr/bin/python
#
# Copyright (c) 2010 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.

'''
Logic for determining if an entitlement certificate has permission to access a particular
URL.

This logic exists in a separate module from the httpd authentication handler to prevent issues
with mod_python imports not being available at unit test time.
'''

import logging

import pulp.certificate


log = logging.getLogger(__name__)

def is_valid(dest, cert_pem):
    '''
    Returns if the specified certificate should be able to access a certain URL.

    @param dest: destination URL trying to be accessed
    @type  dest: string

    @param cert_pem: PEM encoded client certificate sent with the request
    @type  cert_pem: string
    '''

    cert = pulp.certificate.Certificate(content=cert_pem)
    extensions = cert.extensions()

    log.debug('Destination [%s]' % dest)

    valid = False
    for e in extensions:
        if is_download_url_ext(e):
            oid_url = extensions[e]

            log.debug('OID URL     [%s]' % oid_url)

            # This logic isn't final (or really all that good). Need to clean this up when we
            # figure out what the OID values will really look like.
            if oid_url in dest:
                valid = True
                break
            
    return valid

def is_download_url_ext(ext_oid):
    '''
    Tests to see if the given OID corresponds to a download URL value.

    @param ext_oid: OID being tested; cannot be None
    @type  ext_oid: a pulp.certificiate.OID object

    @return: True if the OID contains download URL information; False otherwise
    @rtype:  boolean
    '''
    result = ext_oid.match('1.3.6.1.4.1.2312.9.2.') and ext_oid.match('.1.6')
    return result

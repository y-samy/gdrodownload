import time
import gpsoauth
import requests
import json

class GDriveAgent:
    
    def __init__(self):
        # Set Auth Constants & Credentials
        self.auth_android_id = "DEFAULT_ANDROID_ID"
        self.auth_client_signature = "DEFAULT_CLIENT_SIGNATURE"
        self.auth_app = "com.google.android.apps.docs"
        self.auth_scope = "oauth2:https://www.googleapis.com/auth/drive.readonly"
        self.__set_credentials()
        # Set Access Token
        self.__set_access_token()

    def __set_credentials(self, email="default", master_token="default"):
        if email == "default":
            self.auth_email = 'DEFAULT_EMAIL'
        else:
            self.auth_email = email
        if master_token == "default":
            self.auth_master_token = 'DEFAULT_MASTER_TOKEN'
        else:
            self.auth_master_token = master_token
    
    def __set_access_token(self):
        auth = gpsoauth.perform_oauth(
            self.auth_email,
            self.auth_master_token,
            self.auth_android_id,
            self.auth_scope,
            app = self.auth_app,
            client_sig = self.auth_client_signature
        )
        self.access_token = auth["Auth"]
        self.access_token_expiry = int(auth["Expiry"])

    def __refresh_token(self):
        if self.access_token_expiry < int(time.time()):
            return
        else:
            self.__set_access_token()

    def get_file_metadata(self, file_id):
        self.__refresh_token()
        uri = "https://www.googleapis.com/drive/v2internal/files/{}?supportsAllDrives=true&includePermissionsForView=published&allProperties=false&fields=publishingInfo%28published%29%2cmimeType%2cexportLinks%2cdownloadUrl%2ckind%2cfolderColorRgb%2csharedWithMeDate%2clastViewedByMeDate%2cpermissionsSummary%28visibility%28type%29%29%2ccontentRestrictions%2freadOnly%2cabuseIsAppealable%2cthumbnailVersion%2cheadRevisionId%2cmodifiedDate%2crecency%2cdriveId%2clabels%28starred%2cviewed%2crestricted%2ctrashed%29%2cparent%2fid%2ccreatedDate%2csubscribed%2calternateLink%2cid%2cversion%2cquotaBytesUsed%2cetag%2cdetectors%2cancestorHasAugmentedPermissions%2cfolderFeatures%2cspaces%2ccustomerId%2cabuseNoticeReason%2cworkspaceIds%2ctitle%2cshared%2chasAugmentedPermissions%2cparents%2fid%2cowners%28emailAddressFromAccount%2cid%2corganizationDisplayName%29%2ctrashedDate%2cresourceKey%2corganizationDisplayName%2copenWithLinks%2cdefaultOpenWithLink%2cfileSize%2chasLegacyBlobComments%2cexplicitlyTrashed%2creadersCanSeeComments%2clastModifyingUser%28id%2cemailAddressFromAccount%29%2ccapabilities%28canMoveItemWithinDrive%2ccanTrashChildren%2ccanRemoveChildren%2ccanReadCategoryMetadata%2ccanManageMembers%2ccanTrash%2ccanShare%2ccanAddMyDriveParent%2ccanListChildren%2ccanPrint%2ccanCopy%2ccanDeleteChildren%2ccanDelete%2ccanRename%2ccanModifyContent%2ccanRequestApproval%2ccanBlockOwner%2ccanCopyNonAuthoritative%2ccanReadDrive%2ccanMoveChildrenOutOfDrive%2ccanMoveItemOutOfDrive%2ccanDownload%2ccanShareChildFolders%2ccanChangePermissionExpiration%2ccanAddChildren%2ccanComment%2ccanAcceptOwnership%2ccanEdit%2ccanShareChildFiles%2ccanUntrash%2ccanManageVisitors%2ccanDownloadNonAuthoritative%2ccanChangeSecurityUpdateEnabled%2ccanReportSpamOrAbuse%2ccanMoveChildrenWithinDrive%29%2cactionItems%2cblockingDetectors%2cownedByMe%2cshortcutDetails%28targetResourceKey%2ctargetId%2ctargetMimeType%2ctargetLookupStatus%2ctargetFile%29%2cspamMetadata%28markedAsSpamDate%2cinSpamView%29%2cprimarySyncParentId%2cprimaryDomainName%2csharingUser%28emailAddressFromAccount%2cid%29%2cclientEncryptionDetails%28decryptionMetadata%29%2crecencyReason%2cmd5Checksum%2ccontainsUnsubscribedChildren%2capprovalMetadata%28approvalVersion%2capprovalSummaries%29%2chasThumbnail%2cmodifiedByMeDate%2cpassivelySubscribed&reportPermissionErrors=true&updateViewedDate=true&reason=1351&featureLabel=android-sync-native".format(file_id)
        headers = {"Authorization": "Bearer {}".format(self.access_token)}
        response = requests.get(uri, headers=headers)
        return json.loads(str(response.content, 'utf-8'))
    

    def get_file(self, file_id, file_name):
        self.__refresh_token()
        progress = 0
        uri = "https://www.googleapis.com/download/drive/v2internal/files/{}?alt=media".format(file_id)
        headers = {"Authorization": "Bearer {}".format(self.access_token)}
        with requests.get(uri, headers=headers, stream=True) as response:
            response.raise_for_status()
            with open(file_name, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    progress += len(chunk)
                    file.write(chunk)
                    yield progress
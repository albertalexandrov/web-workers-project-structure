from enum import Enum


class ChannelRedisEnum(Enum):
    DEACTIVATED = "deactivated"
    EMAIL_ROUTING = "email-routing"
    RESEND_PROPOSAL = "resend-proposal"
    DOWNLOAD_PROPOSAL_FILES = "download_proposal_files"
    DOWNLOAD_PROPOSAL_FILE = "download_proposal_file"
    NOTIFY_DECISION_ON_PROPOSAL_RECEIVED = "notify_decision_on_proposal_received"
    EXPORT_PROPOSALS = "export_proposals"
    DELETE_EXPIRED_ACE_FILES = "delete_expired_ace_files"

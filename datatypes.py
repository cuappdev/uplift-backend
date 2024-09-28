from dataclasses import dataclass
from typing import List

@dataclass
class GoogleLoginUser:
    id: str
    email: str
    familyName: str
    givenName: str
    name: str
    photoUrl: str

@dataclass
class AuthRequest:
    idToken: str
    user: GoogleLoginUser
    deviceToken: str

@dataclass
class EditProfileRequest:
    photoUrlBase64: str
    username: str
    venmoHandle: str
    bio: str

@dataclass
class CreateUserRequest:
    username: str
    netid: str
    givenName: str
    familyName: str
    photoUrl: str
    venmoHandle: str
    email: str
    googleId: str
    bio: str

@dataclass
class GetUserByEmailRequest:
    email: str

@dataclass
class SetAdminByEmailRequest:
    email: str
    status: bool

@dataclass
class BlockUserRequest:
    blocked: str

@dataclass
class UnblockUserRequest:
    unblocked: str

@dataclass
class CreatePostRequest:
    title: str
    description: str
    categories: List[str]
    original_price: int
    imagesBase64: List[str]
    userId: str

@dataclass
class GetSearchedPostsRequest:
    keywords: str

@dataclass
class EditPostPriceRequest:
    new_price: int

@dataclass
class CreateFeedbackRequest:
    description: str
    images: List[str]
    userId: str

@dataclass
class GetSearchedFeedbackRequest:
    keywords: str

@dataclass
class FilterPostsRequest:
    category: str

@dataclass
class FilterPostsByPriceRequest:
    lowerBound: int
    upperBound: int

@dataclass
class UploadImageRequest:
    imageBase64: str

@dataclass
class CreateRequestRequest:
    title: str
    description: str
    userId: str

@dataclass
class CreateUserReviewRequest:
    fulfilled: bool
    stars: int
    comments: str
    buyerId: str
    sellerId: str

@dataclass
class ExpoPushMessage:
    to: List[str]
    sound: str
    title: str
    body: str
    data: dict

@dataclass
class SaveTokenRequest:
    token: str
    userId: str

@dataclass
class FindTokensRequest:
    email: str
    title: str
    body: str
    data: dict

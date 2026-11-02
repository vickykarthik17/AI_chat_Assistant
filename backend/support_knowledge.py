import re
from dataclasses import dataclass
from math import log


@dataclass(frozen=True)
class KnowledgeArticle:
    title: str
    source: str
    keywords: tuple[str, ...]
    content: str
    quick_answer: str | None = None
    quick_triggers: tuple[str, ...] = ()


SUPPORT_OFF_TOPIC_REPLY = (
    "I can only help with We-Hive services, plans, onboarding, billing, and support."
)
SUPPORT_NO_ANSWER_REPLY = (
    "I don't have enough approved We-Hive information to answer that. Please check "
    "the relevant page in the application or contact support at +91 8904178434 or "
    "info@we-hive.com."
)

KNOWLEDGE_BASE = (
    KnowledgeArticle(
        title="About We-Hive / Sadhana Mythri",
        source="https://we-hive.com/ and https://we-hive.com/documentation",
        keywords=(
            "we hive", "we-hive", "sadhana mythri", "about", "company",
            "virtual office", "co-working", "coworking", "business presence",
            "business address",
        ),
        content=(
            "We-Hive, also branded Sadhana Mythri, is a subscription-based virtual "
            "office and co-working platform. It helps businesses establish a "
            "professional presence and manage related services online."
        ),
        quick_answer=(
            "We-Hive (Sadhana Mythri) is a virtual-office and co-working platform "
            "that helps businesses establish a professional presence and manage "
            "related services online."
        ),
        quick_triggers=(
            "what is we hive", "what is sadhana mythri",
            "what does we hive do",
        ),
    ),
    KnowledgeArticle(
        title="Advertised platform features",
        source="https://we-hive.com/",
        keywords=(
            "features", "high speed internet", "internet", "security", "privacy",
            "power backup", "official address", "online registration",
            "dashboard", "billing", "management", "mail document management",
            "privacy assured", "24 7 security", "online verification",
            "compliance", "business from anywhere", "secure dashboard",
        ),
        content=(
            "The current home page presents We-Hive as a way to build a business "
            "from anywhere, establish a professional address, streamline compliance, "
            "and manage services flexibly. It advertises high-speed internet, "
            "privacy with 24/7 security, and power backup, and highlights official "
            "business address, online registration and verification, flexible "
            "subscription plans, and a dashboard for billing and management. These "
            "are website claims; confirm location-specific availability and service "
            "conditions with We-Hive before relying on them."
        ),
    ),
    KnowledgeArticle(
        title="Plans, prices, and inclusions",
        source="https://we-hive.com/plans",
        keywords=(
            "plan", "plans", "starter", "growth", "enterprise", "price", "pricing",
            "cost", "monthly", "annual", "annually", "billed annually",
            "business address", "physical workspace", "two wheeler", "parking",
            "printer", "conference room", "freelancer", "freelancers",
            "startup", "startups", "established business", "most popular",
            "popular plan", "subscription duration", "annual total",
        ),
        content=(
            "The public Plans page lists monthly prices billed annually. Starter "
            "Plan, positioned for freelancers: ₹2,999 per month, official business "
            "address and mail/document handling. Growth Plan, marked most popular "
            "and positioned for startups: ₹4,999 per month, those services plus one "
            "physical workspace and two-wheeler parking access. Enterprise Plan: "
            "positioned for established businesses at ₹6,999 per month, those "
            "services plus two physical workspaces, printer and conference-room "
            "access, and reserved two-wheeler parking. The page labels these prices "
            "as monthly rates billed annually. The payment page calculates the "
            "annual amount as monthly price times 12; taxes, if applicable, are "
            "shown by the payment provider."
        ),
        quick_answer=(
            "Starter is ₹2,999/month for freelancers and includes an official "
            "business address and mail/document handling. Growth is ₹4,999/month "
            "(marked most popular, for startups) and adds one physical workspace "
            "and two-wheeler parking access. Enterprise is ₹6,999/month for "
            "established businesses and adds two workspaces, printer and conference "
            "room access, and reserved two-wheeler parking. All prices are monthly "
            "rates billed annually."
        ),
        quick_triggers=(
            "what plans do you offer",
            "what are the plans",
            "list the plans",
            "plan prices",
            "how much does a plan cost", "what are your plans",
            "what is included in starter", "what does starter include",
            "what does growth include", "what does enterprise include",
            "which plan is for freelancers", "which plan is for startups",
            "what plan is for freelancers", "what plan is for startups",
            "which plan is most popular", "what is the annual plan price",
            "which plan is popular for startups",
            "what is the annual price for enterprise",
            "how much is enterprise", "how much is growth", "how much is starter",
        ),
    ),
    KnowledgeArticle(
        title="Services",
        source="https://we-hive.com/documentation",
        keywords=(
            "services", "virtual office address", "business address",
            "business registration support", "gst registration support",
            "mail handling", "document assistance", "document management",
            "support services", "co-working",
        ),
        content=(
            "The application describes services including a virtual business "
            "address, business-registration support, GST-registration support, mail "
            "handling, document assistance, and customer support. Platform "
            "Documentation says users can manage profile, subscriptions, invoices, "
            "payment history, and business information in the dashboard. It "
            "describes secure online payments and GST where required, and advises "
            "strong passwords and two-factor authentication where available. Do "
            "not promise regulatory approval or specific address eligibility; "
            "these depend on service details and applicable requirements."
        ),
        quick_answer=(
            "We-Hive lists a virtual business address, business and GST registration "
            "support, mail handling, document assistance, and customer support. "
            "Eligibility for a particular address or registration depends on the "
            "service and applicable requirements."
        ),
        quick_triggers=(
            "what services do you offer", "what services are available",
            "list your services",
        ),
    ),
    KnowledgeArticle(
        title="Getting started and onboarding",
        source="https://we-hive.com/faq and https://we-hive.com/documentation",
        keywords=(
            "get started", "getting started", "onboarding", "start", "steps",
            "choose plan", "create account", "sign up", "signup", "register",
            "registration", "login", "log in", "verify information",
            "how it works", "virtual office setup", "account confirmation",
        ),
        content=(
            "The site's How It Works section describes login/signup, KYC "
            "verification, choosing a plan, subscription approval, then receiving "
            "and using the virtual office address. The FAQ separately lists choosing "
            "a plan, creating/logging into an account, confirming the on-screen OTP, "
            "and tracking the application in the dashboard. Platform Documentation "
            "describes account creation, information verification, plan selection, "
            "payment, and service activation. The steps can depend on whether the "
            "user is new or already onboarded; follow the current on-screen flow. "
            "The app's OTP is displayed on screen; do not imply SMS/email delivery."
        ),
        quick_answer=(
            "The site describes signing up or logging in, completing KYC and "
            "on-screen OTP verification, choosing a plan, tracking the application, "
            "and proceeding through approval, payment, and activation as prompted. "
            "Follow the current on-screen steps for your account."
        ),
        quick_triggers=(
            "how do i get started", "how can i get started",
            "what are the steps to get started", "how do i sign up",
            "how does the service work", "how do i set up a virtual office",
            "how do i set up virtual office",
        ),
    ),
    KnowledgeArticle(
        title="Account types and account access",
        source="Registration page and backend validation",
        keywords=(
            "account type", "individual", "business account", "register account",
            "password", "login", "sign in", "email", "gmail", "forgot password",
            "reset password", "credentials",
        ),
        content=(
            "The registration form supports Individual and Business account types "
            "and asks for name, email, and a password of at least eight characters. "
            "The home page refers to Gmail, but registration accepts an email "
            "address. The project does not currently implement an email/SMS OTP "
            "provider or password-recovery flow. Never ask a user to send a password, "
            "OTP, or authentication token in chat."
        ),
    ),
    KnowledgeArticle(
        title="On-screen OTP",
        source="OTP page",
        keywords=(
            "otp", "one time password", "sms otp", "email otp", "otp not received",
            "confirm otp", "resend otp",
        ),
        content=(
            "The current OTP page generates a code and displays it on screen for "
            "the user to enter. The page says an SMS or email OTP provider is not "
            "connected yet. A user can generate a new on-screen code if needed."
        ),
        quick_answer=(
            "The current app displays the OTP on the verification page; SMS/email "
            "delivery is not connected yet. Use the displayed code or choose "
            "\"Generate a new OTP\"."
        ),
        quick_triggers=(
            "where do i get the otp", "i did not receive the otp",
            "how do i verify the otp",
            "how does account confirmation work",
            "can i receive otp by sms", "can i receive otp by email",
        ),
    ),
    KnowledgeArticle(
        title="Customer and business details",
        source="Business Details page and API schema",
        keywords=(
            "business details", "customer details", "profile details", "business name",
            "business type", "gst number", "phone number", "address", "city",
            "state", "pincode", "individual customer",
        ),
        content=(
            "Before subscribing, the application asks for customer/business details. "
            "Business accounts provide business type and name; individual accounts "
            "can use personal details. GST number is optional. Phone, address, city, "
            "state, and pincode are collected. These details are personal data; the "
            "assistant must not request them in chat."
        ),
    ),
    KnowledgeArticle(
        title="Government ID / KYC verification",
        source="Dashboard Plans page and verification API",
        keywords=(
            "kyc", "government id", "government identification", "identity",
            "aadhaar", "aadhar", "pan card", "passport", "driving licence",
            "driving license", "voter id", "upload document", "document upload",
            "pdf", "jpg", "jpeg", "png", "5 mb", "verification status",
            "under review", "pending", "declined", "approved",
        ),
        content=(
            "The authenticated user can upload a government ID for admin review. "
            "The UI lists Aadhaar card, PAN card, Passport, Driving licence, and "
            "Voter ID as document types. Accepted file formats are PDF, JPG/JPEG, "
            "and PNG, with a 5 MB maximum. Statuses include not started, pending, "
            "approved, and declined. The assistant cannot inspect uploaded documents "
            "or retrieve a user's individual review decision."
        ),
    ),
    KnowledgeArticle(
        title="Application review and account activation",
        source="https://we-hive.com/faq",
        keywords=(
            "application status", "application review", "review time",
            "activation", "account status", "account under review", "pending review",
            "approval", "approved", "rejected", "application progress",
            "notifications", "admin review", "how long activation takes",
            "processing time", "review duration",
        ),
        content=(
            "Applications and government-ID verification may be reviewed by an "
            "administrator before account activation. The authenticated dashboard "
            "shows account status and applications; notifications are intended for "
            "application-decision updates. The FAQ states that processing depends "
            "on the plan and submitted business details; it does not promise a "
            "fixed activation time. The assistant has no access to any user's live "
            "status."
        ),
        quick_answer=(
            "The FAQ says activation time depends on the plan and submitted "
            "business details; it does not promise a fixed review time. Track your "
            "application in the dashboard or contact support for account-specific "
            "status."
        ),
        quick_triggers=(
            "how long does activation take", "how long will approval take",
            "how long does application review take",
        ),
    ),
    KnowledgeArticle(
        title="Payment methods and checkout",
        source="https://we-hive.com/faq and https://we-hive.com/documentation",
        keywords=(
            "payment", "payments", "pay", "checkout", "razorpay", "upi",
            "credit card", "debit card", "payment failed", "payment status",
            "tax", "gst tax",
        ),
        content=(
            "Payment is collected through the application's secure online checkout "
            "(Razorpay). The FAQ lists UPI and credit/debit cards. The payment page "
            "charges a single annual total equal to the monthly plan price times 12; "
            "taxes, if applicable, are shown by the payment provider. Never share "
            "card details, OTPs, or payment credentials in chat."
        ),
        quick_answer=(
            "The app supports secure online checkout and lists UPI and credit/debit "
            "cards as payment methods. The subscription is billed annually."
        ),
        quick_triggers=(
            "what payment methods do you accept",
            "which payment methods are accepted",
            "how can i pay",
        ),
    ),
    KnowledgeArticle(
        title="Subscriptions, one-plan rule, and renewal",
        source="Dashboard Plans, Invoices, and subscription API",
        keywords=(
            "subscription", "subscriptions", "one plan", "multiple plans",
            "active plan", "renew", "renewal", "expires", "expiry",
            "annual subscription", "change plan", "upgrade plan",
        ),
        content=(
            "The application enforces one active subscription per account. The "
            "portal lets the user view the selected plan, its status and expiry, "
            "and renew an active subscription for another year through payment "
            "checkout. The FAQ says upgrades may be available subject to plan "
            "availability; direct the user to support for an account-specific plan "
            "change. Never claim access to their subscription record."
        ),
    ),
    KnowledgeArticle(
        title="Cancellation",
        source="https://we-hive.com/refunds",
        keywords=(
            "cancel", "cancellation", "cancel subscription", "stop renewal",
            "end plan", "terminate", "non refundable", "non-refundable",
        ),
        content=(
            "The portal includes a cancel-plan action for an active subscription. "
            "The Refund Policy says customers may cancel future renewals at any "
            "time, but cancellation does not automatically entitle them to a refund "
            "for the current billing period. Use the client portal and applicable "
            "plan terms for account-specific cancellation."
        ),
        quick_answer=(
            "The Refund Policy says you may cancel future renewals, but cancellation "
            "does not automatically refund the current billing period. Use the "
            "client portal and review the plan terms."
        ),
        quick_triggers=(
            "can i cancel my subscription", "how do i cancel my subscription",
            "can i cancel future renewals",
        ),
    ),
    KnowledgeArticle(
        title="Invoices and billing history",
        source="FAQ, Documentation, and Invoices page",
        keywords=(
            "invoice", "invoices", "billing", "bill", "payment history",
            "invoice history", "gst invoice", "receipt", "renewal date",
        ),
        content=(
            "The client dashboard includes invoice history and payment information. "
            "The app says an invoice is generated after the first successful payment; "
            "the FAQ says GST-compliant invoices are generated for eligible "
            "subscriptions. The portal displays invoice amount, plan, status, and "
            "date. The assistant cannot retrieve a user's invoice."
        ),
    ),
    KnowledgeArticle(
        title="Refund eligibility and processing",
        source="https://we-hive.com/refunds",
        keywords=(
            "refund", "refunds", "money back", "refund time", "refund status",
            "duplicate payment", "incorrect amount", "unable to provide service",
            "verification fails", "non refundable",
        ),
        content=(
            "Fees are generally non-refundable once service activation or provisioning "
            "has begun. A refund may be considered for duplicate technical charges, "
            "an incorrect amount, inability to provide the purchased service for "
            "reasons solely attributable to Sadhana Mythri, or failed required "
            "verification before activation when the service cannot be provided. "
            "Requests are reviewed case by case with payment details and reason; "
            "approved refunds generally take 7–14 business days via the original "
            "payment method, subject to provider/bank timelines. Change of mind, "
            "partial use, failure to use, incorrect customer information, terms "
            "violations, and policy-related account suspension are generally not "
            "refundable. Eligible requests should include payment details and a "
            "reason; additional documentation may be requested. Requests are "
            "reviewed case by case. Do not promise a refund or determine "
            "individual eligibility."
        ),
        quick_answer=(
            "The Refund Policy says fees are generally non-refundable after "
            "activation or provisioning begins, with limited exceptions such as "
            "duplicate/incorrect charges or inability to provide the service. "
            "Requests are reviewed case by case; approved refunds generally take "
            "7–14 business days. Contact support with payment details and the "
            "reason—eligibility is not guaranteed."
        ),
        quick_triggers=(
            "what is the refund policy", "how long do refunds take",
            "can i get a refund", "when will my refund arrive",
            "how do i request a refund",
        ),
    ),
    KnowledgeArticle(
        title="Privacy and personal data",
        source="https://we-hive.com/privacy",
        keywords=(
            "privacy", "personal data", "information collected", "data collection",
            "sell data", "share data", "cookies", "data retention", "delete data",
            "privacy rights", "security", "children", "under 18",
        ),
        content=(
            "The Privacy Policy says the service may collect contact and business "
            "details, portal activity, and submitted verification documents to "
            "operate the service, communicate with users, support accounts, improve "
            "the experience, and meet legal or regulatory obligations. Personal "
            "information is not sold; limited sharing may occur with "
            "payment processors, authorities when legally required, technology/"
            "hosting providers, professional advisors, and service partners. Cookies "
            "may support preferences, usability, and traffic analysis; disabling "
            "them may affect features. Data is retained as needed for service, "
            "legal obligations, disputes, and agreements. Reasonable technical and "
            "organizational safeguards are used, but internet transmission is not "
            "completely secure. Subject to law, users may "
            "request access, correction, eligible deletion, or withdraw consent. "
            "External websites have their own privacy practices. The service is not "
            "intended for people under 18; the policy may be updated."
        ),
        quick_answer=(
            "The Privacy Policy says We-Hive may collect contact/business details, "
            "portal activity, and verification documents to operate the service and "
            "meet obligations. It says personal data is not sold, though limited "
            "sharing with providers and others may occur. The policy describes "
            "reasonable safeguards, not perfect security."
        ),
        quick_triggers=(
            "what information does we hive collect",
            "what personal information is collected",
            "does we hive sell my data", "how does we hive protect my data",
        ),
    ),
    KnowledgeArticle(
        title="Terms and user eligibility",
        source="https://we-hive.com/terms",
        keywords=(
            "terms", "terms and conditions", "eligibility", "age", "legal",
            "account responsibility", "password security", "lawful business",
            "taxes", "gst charged", "service availability", "suspend account",
            "late payment", "missed payment", "payment due", "due date",
            "pay on time", "do not pay on time",
            "unauthorized access", "intellectual property", "copy website",
            "liability", "governing law", "india", "termination",
            "third party", "suspension",
        ),
        content=(
            "The Terms require users to be at least 18, provide accurate and complete "
            "information, keep credentials confidential, and use services lawfully "
            "for business. Users are responsible for account activity and should "
            "report suspected unauthorized access. Portal/address/billing access "
            "may be limited until onboarding is complete. Fees are paid in advance "
            "unless otherwise agreed; applicable taxes including GST may apply, and "
            "late payment may lead to service suspension or termination. Features, "
            "prices, package contents, and support scope may change; current website "
            "and customer communications are authoritative. The site reserves "
            "maintenance/compliance changes and action against fraud or policy "
            "violations. Site branding, software, and content belong to Sadhana "
            "Mythri or licensors and may not be copied/distributed without "
            "permission. The Terms limit certain damages to the extent allowed by "
            "law, disclaim responsibility for third-party sites/services, and state "
            "that Indian law governs, with disputes heard in competent courts where "
            "Sadhana Mythri is registered or operates. Refer legal interpretations "
            "to the published Terms or qualified counsel."
        ),
        quick_answer=(
            "The Terms require users to be at least 18, provide accurate information, "
            "protect their credentials, and use the service lawfully. Fees are "
            "generally payable in advance; late payment may lead to suspension or "
            "termination. See the current Terms page for the full conditions."
        ),
        quick_triggers=(
            "what are the terms and conditions",
            "what happens if i miss a payment",
            "what happens if i pay late",
            "what happens if i do not pay on time",
            "what is the minimum age",
        ),
    ),
    KnowledgeArticle(
        title="Careers",
        source="https://we-hive.com/careers",
        keywords=(
            "career", "careers", "job", "jobs", "vacancy", "role", "work at",
            "apply for job", "resume", "operations coordinator",
            "customer support associate", "business services specialist",
        ),
        content=(
            "The Careers page welcomes interest in customer support, operations "
            "coordination, document handling, and digital product work. It lists "
            "Customer Support Associate, Operations Coordinator, and Business "
            "Services Specialist as roles of interest. Even when no open roles are "
            "listed, candidates may introduce themselves. Applicants are asked to "
            "send a resume, short introduction, and role of interest; applications "
            "are reviewed manually. The page does not specify a careers submission "
            "email, so direct users to the published contact channels."
        ),
        quick_answer=(
            "The Careers page welcomes interest in Customer Support Associate, "
            "Operations Coordinator, and Business Services Specialist roles. Send "
            "a resume, short introduction, and role of interest using the website's "
            "published contact details; applications are reviewed manually."
        ),
        quick_triggers=(
            "how do i apply for a job", "are there jobs at we hive",
            "what roles are available",
        ),
    ),
    KnowledgeArticle(
        title="Mission and vision",
        source="https://we-hive.com/mission-vision",
        keywords=(
            "mission", "vision", "company goal", "purpose", "business credibility",
            "sadhana mythri mission", "we hive mission", "company mission",
        ),
        content=(
            "The mission is to empower businesses with reliable virtual-office "
            "solutions that simplify operations, build credibility, and enable "
            "sustainable growth. The vision is to become a trusted virtual-office "
            "platform helping businesses establish a professional presence from "
            "anywhere."
        ),
        quick_answer=(
            "We-Hive's mission is to empower businesses with reliable virtual-office "
            "solutions that simplify operations, build credibility, and support "
            "sustainable growth. Its vision is to become a trusted virtual-office "
            "platform helping businesses establish a professional presence from "
            "anywhere."
        ),
        quick_triggers=(
            "what is the mission of sadhana mythri",
            "what is the mission of we hive",
            "what is we hive vision",
        ),
    ),
    KnowledgeArticle(
        title="Contact and support",
        source="https://we-hive.com/faq and https://we-hive.com/support-chat",
        keywords=(
            "contact", "support", "phone", "telephone", "call", "email",
            "info@we-hive.com", "8904178434", "reach", "help desk",
            "24 7 customer support", "24 hours support", "support availability",
            "support chat", "chat session refresh", "clear chat",
        ),
        content=(
            "The FAQ says the support team is available 24/7 for onboarding, "
            "subscriptions, and general questions. The Support Chat page also "
            "offers a chat form, Clear Chat, and direct contact links; it warns "
            "that the session may be lost on page refresh. The home page lists "
            "telephone +91 8904178434 and info@we-hive.com. Use those published "
            "channels for issues requiring account-specific help."
        ),
        quick_answer=(
            "The FAQ says support is available 24/7 for onboarding, subscriptions, "
            "and general questions. Contact We-Hive at +91 8904178434 or "
            "info@we-hive.com."
        ),
        quick_triggers=(
            "how can i contact support", "contact support",
            "how do i contact support",
            "how do i contact the support team",
            "what is your support phone number", "what is your support email",
            "is support available 24 7", "does we hive have 24 7 support",
            "does we hive offer 24 7 customer support",
            "is customer support available 24 7",
            "does the website provide 24 7 customer support",
            "does the website provide 24 7 customer support to users",
        ),
    ),
    KnowledgeArticle(
        title="Who the service is for",
        source="https://we-hive.com/faq and https://we-hive.com/plans",
        keywords=(
            "who can use", "who is it for", "target customer", "freelancer",
            "freelancers", "startup", "startups", "entrepreneur", "entrepreneurs",
            "small business", "established business", "companies", "business types",
        ),
        content=(
            "The FAQ says the services are designed for startups, freelancers, "
            "entrepreneurs, small businesses, and companies looking for a "
            "professional business presence. The Plans page positions Starter for "
            "freelancers, Growth for startups, and Enterprise for established "
            "businesses. The home page currently states that more than 1,000 "
            "businesses trust WE-HIVE; treat this as a website-reported promotional "
            "figure, not independently verified data."
        ),
        quick_answer=(
            "The FAQ describes the service as suitable for startups, freelancers, "
            "entrepreneurs, small businesses, and companies. The Plans page positions "
            "Starter for freelancers, Growth for startups, and Enterprise for "
            "established businesses."
        ),
        quick_triggers=(
            "who can use sadhana mythri", "who is we hive for",
            "which businesses can use we hive",
        ),
    ),
    KnowledgeArticle(
        title="Company identity and public office address",
        source="https://we-hive.com/",
        keywords=(
            "company identity", "company name", "legal entity", "registered office",
            "office address", "business address", "hyderabad", "telangana",
            "postal address", "facebook", "instagram", "twitter", "social media",
            "contact details",
        ),
        content=(
            "The home page identifies WE-HIVE and names SADHANA MYTHRI PROPERTIES "
            "LLP in its office-address section. The published office address is "
            "11-13-1377/2/410 Alkp Cly, Vsvi Cly, Ydv Ngr, Saroornagar, Saroornagar, "
            "Hyderabad, Hyderabad-500035, Telangana, India. This is the website's "
            "office address; do not assume it is the service/workspace address "
            "available under a particular plan. The footer links Facebook at "
            "facebook.com/profile.php?id=61594802775277, Instagram at "
            "instagram.com/we_hive, and X at x.com/Wehive_2026."
        ),
        quick_answer=(
            "SADHANA MYTHRI PROPERTIES LLP 11-13-1377/2/410 Alkp Cly, Vsvi Cly, "
            "Ydv Ngr, Saroornagar, Saroornagar, Hyderabad, Hyderabad- 500035, "
            "Telangana, India"
        ),
        quick_triggers=(
            "what is the office address", "where is we hive office",
            "what is the registered office address",
            "what is the office address in hyderabad",
            "what is your office address", "our office address",
            "actual office address", "tell me the office address",
            "give me the office address", "where is the office located",
        ),
    ),
    KnowledgeArticle(
        title="Public pages and portal features",
        source="Frontend routes and portal pages",
        keywords=(
            "dashboard", "portal", "profile", "applications", "notifications",
            "my plan", "settings", "billing history", "support chat", "website pages",
            "faq", "documentation", "refund policy",
        ),
        content=(
            "Public pages include Home, Plans, FAQ, Documentation, Terms & "
            "Conditions, Privacy Policy, Refund Policy, Careers, Mission & Vision, "
            "and Support Chat. The customer portal has Dashboard, Profile, "
            "Applications, Plans/KYC, Invoices & Billing, and Notifications. "
            "Notifications currently displays an empty-state message until updates "
            "are available. Authenticated portal data is private and the assistant "
            "cannot read it."
        ),
    ),
)

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a", "an", "and", "are", "be", "by", "can", "do", "does", "for", "how",
    "i", "if", "in", "is", "it", "me", "my", "of", "on", "or", "the", "this",
    "that", "to", "we", "what", "when", "where", "which", "who", "with", "you",
    "your",
}


def normalize(text: str) -> str:
    return " ".join(TOKEN_PATTERN.findall(text.casefold()))


def retrieve_support_knowledge(
    message: str, limit: int = 3
) -> tuple[KnowledgeArticle, ...]:
    normalized_message = normalize(message)
    query_tokens = {
        token for token in normalized_message.split() if token not in STOP_WORDS
    }
    if not query_tokens or limit <= 0:
        return ()

    documents = [
        set(
            normalize(f"{article.title} {' '.join(article.keywords)}").split()
        )
        for article in KNOWLEDGE_BASE
    ]
    document_frequencies = {
        token: sum(token in document for document in documents)
        for token in query_tokens
    }

    scored: list[tuple[float, int, KnowledgeArticle]] = []
    for position, article in enumerate(KNOWLEDGE_BASE):
        title_tokens = set(normalize(article.title).split())
        keyword_tokens = set(
            normalize(" ".join(article.keywords)).split()
        ) - STOP_WORDS
        content_tokens = set(normalize(article.content).split()) - STOP_WORDS
        score = 0.0
        for token in query_tokens:
            frequency = document_frequencies[token]
            inverse_document_frequency = log(
                1 + (len(KNOWLEDGE_BASE) - frequency + 0.5) / (frequency + 0.5)
            )
            if token in title_tokens:
                score += 4.0 * inverse_document_frequency
            elif token in keyword_tokens:
                score += 2.5 * inverse_document_frequency
            elif token in content_tokens:
                score += 0.35 * inverse_document_frequency

        for keyword in article.keywords:
            normalized_keyword = normalize(keyword)
            if " " in normalized_keyword and (
                f" {normalized_keyword} " in f" {normalized_message} "
            ):
                score += 2.0

        if score:
            scored.append((score, -position, article))

    scored.sort(reverse=True, key=lambda match: (match[0], match[1]))
    if not scored:
        return ()

    minimum_score = scored[0][0] * 0.3
    return tuple(
        article
        for score, _, article in scored
        if score >= minimum_score
    )[:limit]


def quick_support_answer(message: str) -> str | None:
    normalized_message = normalize(message)
    message_tokens = set(normalized_message.split())
    allowed_extra_tokens = {
        "at", "for", "hive", "in", "is", "my", "please", "tell", "the",
        "we", "what", "you", "your",
    }
    broad_markers = {"everything", "overview", "summarize", "summary"}
    requested_topics = sum(
        bool(topic_tokens & message_tokens)
        for topic_tokens in (
            {"plan", "plans", "price", "prices", "pricing", "cost"},
            {"feature", "features", "service", "services"},
            {"start", "started", "starting", "onboarding", "signup"},
        )
    )
    is_we_hive_overview = (
        bool(message_tokens & broad_markers)
        and bool(message_tokens & {"hive", "sadhana", "platform", "application"})
    )
    if is_we_hive_overview or requested_topics >= 3:
        return (
            "We-Hive (Sadhana Mythri) is a virtual-office and co-working platform "
            "for establishing a professional business presence. Its website "
            "highlights an official business address, online registration and "
            "verification, flexible plans, and a dashboard for billing and "
            "management. It also advertises high-speed internet, privacy with "
            "24/7 security, and power backup; confirm location-specific availability "
            "with We-Hive.\n\n"
            "Plans (monthly rates billed annually): Starter is ₹2,999/month for "
            "freelancers and includes an official business address and mail/document "
            "handling. Growth is ₹4,999/month (marked most popular, for startups) "
            "and adds one physical workspace and two-wheeler parking access. "
            "Enterprise is ₹6,999/month for established businesses and adds two "
            "physical workspaces, printer and conference-room access, and reserved "
            "two-wheeler parking. The annual payment is the monthly rate × 12; "
            "applicable taxes are shown at checkout.\n\n"
            "To get started, create an account or log in, follow the on-screen "
            "verification and business-details steps, complete KYC as requested, "
            "choose a plan, then follow the application review, payment, and "
            "activation steps shown in the portal. OTP is displayed on screen; "
            "SMS/email delivery is not connected."
        )

    matches = [
        article
        for article in KNOWLEDGE_BASE
        if article.quick_answer
        and any(
            f" {normalize(trigger)} " in f" {normalized_message} "
            and message_tokens
            <= set(normalize(trigger).split()) | allowed_extra_tokens
            for trigger in article.quick_triggers
        )
    ]
    if len(matches) == 1:
        return matches[0].quick_answer
    return None

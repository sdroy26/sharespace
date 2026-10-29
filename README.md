# ShareSpace — Trusted Resource Sharing Platform

**ShareSpace** is a Django-based web application designed to help institutions and communities share underutilised spaces, equipment, and technical resources through a structured, transparent, and accountable borrowing process.

The platform focuses on the complete resource-sharing lifecycle, from resource discovery and booking requests to approval, check-in, return, and record keeping.

## Problem Statement

Educational institutions, laboratories, makerspaces, and community organisations often have valuable resources that remain unused, while students, researchers, and creators may struggle to access them affordably.

Informal booking processes can lead to scheduling conflicts, unclear eligibility requirements, incomplete borrowing records, and difficulty tracking damage or overdue returns.

ShareSpace aims to organise this process in one application while supporting resource-owner control, responsible access, and accountability.

## Key Features

- **Resource Management:** Organise information about shared resources.
- **Resource Discovery:** Help users find resources that meet their needs.
- **Booking Requests:** Allow users to request access to resources.
- **Eligibility and Availability Checks:** Support validation of applicable booking requirements.
- **Approval Workflow:** Allow authorised owners or managers to review requests.
- **Check-In and Return:** Support the resource handover and return lifecycle.
- **Condition Reporting:** Record resource condition where implemented.
- **Incident Tracking:** Support recording issues such as damage or delays where implemented.
- **Notifications:** Communicate relevant booking events where configured.
- **Audit History:** Support traceability of important actions where implemented.
- **Fair Resource Access:** Provide a foundation for transparent allocation and usage policies.

*Note: The availability of individual features depends on the implementation in the submitted version of the project.*

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Django |
| Frontend | HTML, CSS, Django Templates |
| Browser Interactions | Vanilla JavaScript |
| Database — local development | SQLite |
| Database — intended production | PostgreSQL, when configured |
| Application Routing | Django URL configuration |
| Data Access | Django ORM |

## Project Structure

```text
ShareSpace/
├── manage.py
├── requirements.txt
├── config/
├── accounts/
├── resources/
├── bookings/
├── operations/
├── audit/
├── notifications/
├── core/
├── templates/
├── static/
└── README.md
```

The exact files and directories may vary depending on the current repository version.

## Getting Started

### Prerequisites

- Python installed
- Git installed if cloning the repository
- A terminal or command prompt

### 1. Clone the Repository

Replace the placeholder with your public GitHub repository URL.

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <PROJECT_DIRECTORY>
```

Run the remaining commands from the directory containing `manage.py`.

### 2. Create a Virtual Environment

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Load Demo Data (If Available)

If the project includes the `seed_demo` management command:

```bash
python manage.py seed_demo
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

Open the local development address printed in your terminal.

## Testing and Validation

Run Django's configuration checks:

```bash
python manage.py check
```

Run the automated test suite:

```bash
python manage.py test
```

These commands should be executed before submission. Their inclusion in this README does not imply that the tests have already passed.

## How ShareSpace Works

The intended resource-sharing workflow is:

1. An authorised owner lists a resource and defines its usage conditions.
2. A borrower discovers the resource and reviews the requirements.
3. The borrower submits a booking request.
4. The application validates the applicable requirements.
5. The owner or authorised manager reviews the request.
6. The request is approved, rejected, or handled through a waiting list if supported.
7. The handover and initial condition are recorded where supported.
8. The resource is used and returned.
9. The return condition and any relevant incidents are recorded where supported.
10. Authorised users can review the available transaction history.

## Security and Privacy

The application is intended to support responsible resource sharing through appropriate access controls and server-side validation.

For deployment and use:

- Keep secret keys and credentials out of source control.
- Configure production settings securely.
- Disable Django debug mode in production.
- Configure allowed hosts correctly.
- Use a persistent production database.
- Restrict access to personal information and operational records.
- Use fictional or authorised demonstration data.

## Deployment

ShareSpace can be deployed to a hosting platform that supports its Django configuration.

A production deployment may require:

- Production environment variables
- A persistent database such as PostgreSQL
- Correct static-file configuration
- Database migrations
- Secure host and debug settings
- Verification of the main booking workflow

The application should be tested after deployment before a live URL is shared.

## Limitations and Future Improvements

Potential future improvements include:

- More advanced resource search and filtering
- Stronger eligibility and training verification
- Improved waiting-list and fair-allocation policies
- More comprehensive notifications
- Resource utilisation reporting
- Enhanced audit and incident management
- Additional automated tests
- Production monitoring and backup procedures
- Optional AI-assisted resource matching, with appropriate human oversight

These items represent potential improvements and should not be interpreted as existing functionality unless implemented.

## AI and External Services

The described application uses conventional Django request handling, validation, database operations, and rendered responses. No AI model, agent framework, or prompt pipeline is identified in the current project description.

Any external services or AI tools actually used during development should be disclosed in the final submission.

## Team Contributions

Add the actual names and contributions of each team member.

- **Contributor 1:** [Describe the frontend or UI work personally completed.]
- **Contributor 2:** [Describe the backend, database, or workflow work personally completed.]

Contributions should accurately reflect each member's work.

## Project Links

- **GitHub Repository:** [Insert repository URL]
- **Live Demo:** [Insert working deployment URL]
- **Project Report:** [Insert publicly accessible PDF URL]

## Acknowledgements

Developed as a resource-sharing solution for the hackathon challenge **“Unlock Underused Equipment and Spaces.”**


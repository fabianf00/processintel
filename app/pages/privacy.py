import streamlit as st

_, content_column, _ = st.columns([1, 3, 1])
with content_column:

    st.markdown(
        """## Privacy Policy

This Privacy Policy explains how personal data are processed when using the ProcessIntel application.

### 1. Controller

The controller responsible for data processing pursuant to Art. 4(7) GDPR is:

SWISDATA gGmbH  
Media Quarter 3.4 / 5th Floor  
Maria-Jacobi-Gasse 1  
A-1030 Vienna  
Austria  
Email: office@swisdata.eu

---

### 2. Server Log Data (NGINX Metadata)

When accessing the ProcessIntel application, data are processed for technical necessity in server log files (NGINX), including:

- IP address
- Date and time of access
- Accessed resources (URLs / endpoints)
- Technical connection and protocol data
- Client data (browser, operating system / user agent)

These data are processed to ensure the secure and reliable operation of the application.

Legal basis: Art. 6(1)(f) GDPR (legitimate interest).  
No personal profiling or individual evaluation takes place.

Log data may be used only in anonymized form for technical or statistical analysis.

---

### 3. Temporary Processing of Uploaded Data

Uploaded data are processed exclusively on a temporary basis:

- Storage solely for technical processing
- Automatic deletion after a maximum of 2 hours
- No permanent storage
- No further processing or disclosure

Legal basis: Art. 6(1)(b) GDPR.

---

### 4. Data Sharing and Hosting

No personal data are shared with third parties. All services operate on own hardware. No data are transferred outside the EU/EEA.

---

### 5. Cookies

The ProcessIntel application uses cookies solely for technical necessity.

These cookies are required to ensure the secure and proper operation of the application (e.g. session management). No cookies are used for tracking, analytics, marketing, or profiling purposes.
    """
    )

⠴ Loading rules...                                                                                                                
  Scanning 19 files (only git-tracked) with 2884 Code rules, 16289 Supply Chain rules:
            
  CODE RULES
                                                                                                                        
  Language      Rules   Files          Origin      Rules                                                                
 ─────────────────────────────        ───────────────────                                                               
  <multilang>      60      19          Pro rules    1824                                                                
  python         1156      10          Community    1060                                                                
  js              323       1                                                                                           
  yaml             31       1                                                                                           
  html              2       1                                                                                           
                                                                                                                        
                    
  SUPPLY CHAIN RULES
                                                                                                                        
  Dependency Sources       Resolution Method   Ecosystem   Dependencies   Rules                                         
 ───────────────────────────────────────────────────────────────────────────────                                        
  week6/requirements.txt   Lockfile            Pypi        9              16289                                         
                                                                                                                        
                                                                                                                        
  Analysis       Rules                                                                                                  
 ──────────────────────                                                                                                 
  Basic          15132                                                                                                  
  Reachability    1157                                                                                                  
                                                                                                                        
          
  PROGRESS
   
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00                                                                                                                        
  Uploading scan results  
  Finalizing scan                                                                                                                                 
                                    
                                    
┌──────────────────────────────────┐
│ 1 Reachable Supply Chain Finding │
└──────────────────────────────────┘
                                         
    week6/requirements.txt
   ❯❯❱ werkzeug - CVE-2024-34069
          Severity: HIGH                                                                            
          Affected versions of Werkzeug are vulnerable to Cross-Site Request Forgery (CSRF). Exploitation     
          requires the attacker to guess a URL in the developer's application that will trigger the debugger  
          AND requires the attacker to get the developer to interact with a domain and subdomain they control,
          and enter the debugger PIN.                                                                         
                                                                                                              
           ▶▶┆ Fixed for werkzeug at version: 3.0.3
            9┆ Werkzeug==0.14.1
                                         
                                         
┌───────────────────────────────────────┐
│ 17 Undetermined Supply Chain Findings │
└───────────────────────────────────────┘
                                         
    week6/requirements.txt
    ❯❱ pydantic - CVE-2024-3772
          Severity: MODERATE                                                              
          Affected versions of pydantic are vulnerable to Inefficient Regular Expression Complexity.
                                                                                                    
           ▶▶┆ Fixed for pydantic at versions: 1.10.13, 2.4.0
            4┆ pydantic==1.5.1
   
    ❯❱ pydantic - CVE-2021-29510
          Severity: MODERATE                                                                   
          Affected versions of pydantic are vulnerable to Loop with Unreachable Exit Condition ('Infinite
          Loop').                                                                                        
                                                                                                         
           ▶▶┆ Fixed for pydantic at versions: 1.6.2, 1.7.4, 1.8.2
            4┆ pydantic==1.5.1
   
    ❯❱ requests - CVE-2024-35195
          Severity: MODERATE                                                                 
          Affected versions of requests are vulnerable to Always-Incorrect Control Flow Implementation.
                                                                                                       
           ▶▶┆ Fixed for requests at version: 2.32.0
            5┆ requests==2.19.1
   
    ❯❱ requests - CVE-2023-32681
          Severity: MODERATE                                                                        
          Affected versions of requests are vulnerable to Exposure of Sensitive Information to an Unauthorized
          Actor.                                                                                              
                                                                                                              
           ▶▶┆ Fixed for requests at version: 2.31.0
            5┆ requests==2.19.1
   
    ❯❱ requests - CVE-2024-47081
          Severity: MODERATE                                                         
          Affected versions of requests are vulnerable to Insufficiently Protected Credentials.
                                                                                               
           ▶▶┆ Fixed for requests at version: 2.32.4
            5┆ requests==2.19.1
   
    ❯❱ requests - CVE-2026-25645
          Severity: MODERATE                                            
          Affected versions of requests are vulnerable to Insecure Temporary File.
                                                                                  
           ▶▶┆ Fixed for requests at version: 2.33.0
            5┆ requests==2.19.1
   
    ❯❱ jinja2 - CVE-2024-34064
          Severity: MODERATE                                                                  
          Affected versions of Jinja2 are vulnerable to Improper Neutralization of Input During Web Page
          Generation ('Cross-site Scripting').                                                          
                                                                                                        
           ▶▶┆ Fixed for jinja2 at version: 3.1.4
            7┆ Jinja2==2.10.1
   
    ❯❱ jinja2 - CVE-2025-27516
          Severity: MODERATE                                                                       
          Affected versions of Jinja2 are vulnerable to Improper Neutralization of Special Elements Used in a
          Template Engine.                                                                                   
                                                                                                             
           ▶▶┆ Fixed for jinja2 at version: 3.1.6
            7┆ Jinja2==2.10.1
   
    ❯❱ jinja2 - CVE-2024-22195
          Severity: MODERATE                                                                  
          Affected versions of jinja2 are vulnerable to Improper Neutralization of Input During Web Page
          Generation ('Cross-site Scripting').                                                          
                                                                                                        
           ▶▶┆ Fixed for jinja2 at version: 3.1.3
            7┆ Jinja2==2.10.1
   
    ❯❱ jinja2 - CVE-2024-56326
          Severity: MODERATE                                               
          Affected versions of jinja2 are vulnerable to Protection Mechanism Failure.
                                                                                     
           ▶▶┆ Fixed for jinja2 at version: 3.1.5
            7┆ Jinja2==2.10.1
   
    ❯❱ jinja2 - CVE-2020-28493
          Severity: MODERATE                                                    
          Affected versions of Jinja2 are vulnerable to Uncontrolled Resource Consumption.
                                                                                          
           ▶▶┆ Fixed for jinja2 at version: 2.11.3
            7┆ Jinja2==2.10.1
   
    ❯❱ werkzeug - CVE-2026-27199
          Severity: MODERATE                                                              
          Affected versions of werkzeug are vulnerable to Improper Handling of Windows Device Names.
                                                                                                    
           ▶▶┆ Fixed for werkzeug at version: 3.1.6
            9┆ Werkzeug==0.14.1
   
    ❯❱ werkzeug - CVE-2024-49767
          Severity: MODERATE                                                                
          Affected versions of Quart and Werkzeug are vulnerable to Uncontrolled Resource Consumption.
                                                                                                      
           ▶▶┆ Fixed for werkzeug at version: 3.0.6
            9┆ Werkzeug==0.14.1
   
     ❱ werkzeug - CVE-2023-23934
          Severity: LOW                                                   
          Affected versions of Werkzeug are vulnerable to Improper Input Validation.
                                                                                    
           ▶▶┆ Fixed for werkzeug at version: 2.2.3
            9┆ Werkzeug==0.14.1
   
    ❯❱ werkzeug - CVE-2024-49766
          Severity: MODERATE                                                                     
          Affected versions of Werkzeug are vulnerable to Improper Limitation of a Pathname to a Restricted
          Directory ('Path Traversal').                                                                    
                                                                                                           
           ▶▶┆ Fixed for werkzeug at version: 3.0.6
            9┆ Werkzeug==0.14.1
   
    ❯❱ werkzeug - CVE-2025-66221
          Severity: MODERATE                                                              
          Affected versions of werkzeug are vulnerable to Improper Handling of Windows Device Names.
                                                                                                    
           ▶▶┆ Fixed for werkzeug at version: 3.1.4
            9┆ Werkzeug==0.14.1
   
    ❯❱ werkzeug - CVE-2026-21860
          Severity: MODERATE                                                              
          Affected versions of Werkzeug are vulnerable to Improper Handling of Windows Device Names.
                                                                                                    
           ▶▶┆ Fixed for werkzeug at version: 3.1.5
            9┆ Werkzeug==0.14.1
                                       
                                       
┌─────────────────────────────────────┐
│ 8 Unreachable Supply Chain Findings │
└─────────────────────────────────────┘
                                         
    week6/requirements.txt
   ❯❯❱ requests - CVE-2018-18074
          Severity: HIGH                                                                           
          requests versions before and including 2.19.1 are vulnerable to Insufficiently Protected           
          Credentials. When an HTTP Authorization header is sent to an HTTPS URI, the server can respond with
          a 302 redirect to a plain HTTP server with the same hostname. Requests will then forward the       
          Authorization header to the HTTP server, leaking the contents of the header on an unencrypted      
          connection.                                                                                        
                                                                                                             
           ▶▶┆ Fixed for requests at version: 2.20.0
            5┆ requests==2.19.1
   
   ❯❯❯❱ pyyaml - CVE-2020-1747
          Severity: CRITICAL                                                       
          pyyaml before 5.3.1 is vulnerable to remote code injection. Use `yaml.safe_load` or
          `Loader=SafeLoader`, or upgrade to pyyaml 5.3.1.                                   
                                                                                             
           ▶▶┆ Fixed for pyyaml at version: 5.3.1
            6┆ PyYAML==5.1
   
   ❯❯❯❱ pyyaml - CVE-2020-14343
          Severity: CRITICAL                                                     
          PyYAML before 5.4 is vulnerable to remote code injection. Use `yaml.safe_load` or
          `Loader=SafeLoader`, or upgrade to PyYAML 5.4.                                   
                                                                                           
           ▶▶┆ Fixed for pyyaml at version: 5.4
            6┆ PyYAML==5.1
   
   ❯❯❯❱ pyyaml - CVE-2019-20477
          Severity: CRITICAL                                                                      
          pyyaml before 5.2 is vulnerable to OS command injection via deserialization of untrusted data. Use
          `yaml.safe_load` or `Loader=SafeLoader`, or upgrade to pyyaml 5.2.                                
                                                                                                            
           ▶▶┆ Fixed for pyyaml at version: 5.2
            6┆ PyYAML==5.1
   
    ❯❱ werkzeug - CVE-2023-46136
          Severity: MODERATE                                                                        
          Affected versions of werkzeug are vulnerable to Uncontrolled Resource Consumption / Out-Of-Bounds   
          Write. An attacker can execute a Denial of Service (DoS) attack by sending crafted multipart data to
          an endpoint that parses it. The excessive CPU time and RAM required can hinder worker processes,    
          leading to exhaustion or termination with many concurrent requests.                                 
                                                                                                              
           ▶▶┆ Fixed for werkzeug at versions: 2.3.8, 3.0.1
            9┆ Werkzeug==0.14.1
   
   ❯❯❱ werkzeug - CVE-2019-14322
          Severity: HIGH                                                                           
          Affected versions of werkzeug are vulnerable to Improper Limitation of a Pathname to a Restricted  
          Directory ('Path Traversal'). The SharedDataMiddleware in Werkzeug improperly handles drive letters
          on Windows, potentially allowing an attacker to craft path requests that bypass filesystem access  
          controls, leading to unauthorized file access.                                                     
                                                                                                             
           ▶▶┆ Fixed for werkzeug at version: 0.15.5
            9┆ Werkzeug==0.14.1
   
   ❯❯❱ werkzeug - CVE-2023-25577
          Severity: HIGH                                                                          
          Werkzeug versions before 2.2.3 are vulnerable to denial of service via uncontrolled resource      
          consumption due to werkzeug's multipart form data parser not having a limit for number of parts. A
          request made to an endpoint utilizing accesses request.data, request.form, request.files, or      
          request.get_data(parse_form_data=False) can cause unexpectedly high resource usage. Upgrade to    
          werkzeug version 2.2.3.                                                                           
                                                                                                            
           ▶▶┆ Fixed for werkzeug at version: 2.2.3
            9┆ Werkzeug==0.14.1
   
   ❯❯❱ werkzeug - CVE-2019-14806
          Severity: HIGH                                                                          
          Affected versions of werkzeug are vulnerable to Insufficient Entropy. Insufficient randomness in  
          Werkzeug's interactive debugger PIN when run inside Docker containers sharing the same machine ID.
          An attacker who can reach the debugger interface can predict or brute-force the PIN, bypass its   
          protection and execute arbitrary code.                                                            
                                                                                                            
           ▶▶┆ Fixed for werkzeug at version: 0.15.3
            9┆ Werkzeug==0.14.1
                                 
                                 
┌───────────────────────────────┐
│ 12 Non-blocking Code Findings │
└───────────────────────────────┘
                                            
    week6/backend/app/main.py
    ❯❱ python.fastapi.security.wildcard-cors.wildcard-cors
          CORS policy allows any origin (using wildcard '*'). This is insecure and should be avoided.
          Details: https://sg.run/KxApY                                                              
                                                                                                     
           24┆ allow_origins=["*"],
    
    
          Taint comes from:
    
           24┆ allow_origins=["*"],
    
    
                This is how taint reaches the sink:
    
           24┆ allow_origins=["*"],
    
                                                            
    week6/backend/app/routers/action_items.py
   ❯❯❯❱ python.fastapi.db.generic-sql-fastapi.generic-sql-fastapi
          Untrusted input might be used to build a database query, which can lead to a SQL injection       
          vulnerability. An attacker can execute malicious SQL statements and gain unauthorized access to  
          sensitive data, modify, delete data, or execute arbitrary system commands. The driver API has the
          ability to bind parameters to the query in a safe way. Make sure not to dynamically create SQL   
          queries from user-influenced inputs. If you cannot avoid this, either escape the data properly or
          create an allowlist to check the value.                                                          
          Details: https://sg.run/v8ypl                                                                    
                                                                                                           
           33┆ rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    
    
          Taint comes from:
    
           18┆ skip: int = 0,
    
    
          Taint flows through these intermediate variables:
    
           18┆ skip: int = 0,
    
    
                This is how taint reaches the sink:
    
           33┆ rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    
                                                     
    week6/backend/app/routers/notes.py
   ❯❯❯❱ python.fastapi.db.generic-sql-fastapi.generic-sql-fastapi
          Untrusted input might be used to build a database query, which can lead to a SQL injection       
          vulnerability. An attacker can execute malicious SQL statements and gain unauthorized access to  
          sensitive data, modify, delete data, or execute arbitrary system commands. The driver API has the
          ability to bind parameters to the query in a safe way. Make sure not to dynamically create SQL   
          queries from user-influenced inputs. If you cannot avoid this, either escape the data properly or
          create an allowlist to check the value.                                                          
          Details: https://sg.run/v8ypl                                                                    
                                                                                                           
           33┆ rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    
    
          Taint comes from:
    
           18┆ skip: int = 0,
    
    
          Taint flows through these intermediate variables:
    
           18┆ skip: int = 0,
    
    
                This is how taint reaches the sink:
    
           33┆ rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    
    
            ⋮┆----------------------------------------
   
   ❯❯❱ python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text
          sqlalchemy.text passes the constructed SQL statement to the database mostly unchanged. This means  
          that the usual SQL injection protections are not applied and this function is vulnerable to SQL    
          injection if user input can reach here. Use normal SQLAlchemy operators (such as `or_()`, `and_()`,
          etc.) to construct SQL.                                                                            
          Details: https://sg.run/yP1O                                                                       
                                                                                                             
           71┆ sql = text(
           72┆     f"""
           73┆     SELECT id, title, content, created_at, updated_at
           74┆     FROM notes
           75┆     WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
           76┆     ORDER BY created_at DESC
           77┆     LIMIT 50
           78┆     """
           79┆ )
    
    
          Taint comes from:
    
           75┆ WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
    
    
                This is how taint reaches the sink:
    
           71┆ sql = text(
    
           72┆     f"""
    
           73┆     SELECT id, title, content, created_at, updated_at
    
           74┆     FROM notes
    
           75┆     WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
    
           76┆     ORDER BY created_at DESC
    
           77┆     LIMIT 50
    
           78┆     """
    
           79┆ )
    
    
            ⋮┆----------------------------------------
   
   ❯❯❯❱ python.fastapi.db.sqlalchemy-fastapi.sqlalchemy-fastapi
          Untrusted input might be used to build a database query, which can lead to a SQL injection       
          vulnerability. An attacker can execute malicious SQL statements and gain unauthorized access to  
          sensitive data, modify, delete data, or execute arbitrary system commands. Use the SQLAlchemy ORM
          provided functions to build SQL queries instead to avoid SQL injection.                          
          Details: https://sg.run/L1n29                                                                    
                                                                                                           
           72┆ f"""
           73┆ SELECT id, title, content, created_at, updated_at
           74┆ FROM notes
           75┆ WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
           76┆ ORDER BY created_at DESC
           77┆ LIMIT 50
           78┆ """
    
    
          Taint comes from:
    
           70┆ def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
    
    
          Taint flows through these intermediate variables:
    
           70┆ def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
    
    
                This is how taint reaches the sink:
    
           72┆ f"""
    
           73┆ SELECT id, title, content, created_at, updated_at
    
           74┆ FROM notes
    
           75┆ WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
    
           76┆ ORDER BY created_at DESC
    
           77┆ LIMIT 50
    
           78┆ """
    
    
            ⋮┆----------------------------------------
   
   ❯❯❯❱ python.fastapi.db.generic-sql-fastapi.generic-sql-fastapi
          Untrusted input might be used to build a database query, which can lead to a SQL injection       
          vulnerability. An attacker can execute malicious SQL statements and gain unauthorized access to  
          sensitive data, modify, delete data, or execute arbitrary system commands. The driver API has the
          ability to bind parameters to the query in a safe way. Make sure not to dynamically create SQL   
          queries from user-influenced inputs. If you cannot avoid this, either escape the data properly or
          create an allowlist to check the value.                                                          
          Details: https://sg.run/v8ypl                                                                    
                                                                                                           
           80┆ rows = db.execute(sql).all()
    
    
          Taint comes from:
    
           70┆ def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
    
    
          Taint flows through these intermediate variables:
    
           70┆ def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
    
           71┆ sql = text(
    
    
                This is how taint reaches the sink:
    
           80┆ rows = db.execute(sql).all()
    
    
            ⋮┆----------------------------------------
   
   ❯❯❯❱ python.fastapi.code.tainted-code-stdlib-fastapi.tainted-code-stdlib-fastapi
          The application might dynamically evaluate untrusted input, which can lead to a code injection    
          vulnerability. An attacker can execute arbitrary code, potentially gaining complete control of the
          system. To prevent this vulnerability, avoid executing code containing user input. If this is     
          unavoidable, validate and sanitize the input, and use safe alternatives for evaluating user input.
          Details: https://sg.run/L1qDX                                                                     
                                                                                                            
          104┆ result = str(eval(expr))  # noqa: S307
    
    
          Taint comes from:
    
          103┆ def debug_eval(expr: str) -> dict[str, str]:
    
    
          Taint flows through these intermediate variables:
    
          103┆ def debug_eval(expr: str) -> dict[str, str]:
    
    
                This is how taint reaches the sink:
    
          104┆ result = str(eval(expr))  # noqa: S307
    
    
            ⋮┆----------------------------------------
   
    ❯❱ python.lang.security.audit.eval-detected.eval-detected
          Detected the use of eval(). eval() can be dangerous if used to evaluate dynamic content. If this 
          content can be input from outside the program, this may be a code injection vulnerability. Ensure
          evaluated content is not definable by external sources.                                          
          Details: https://sg.run/ZvrD                                                                     
                                                                                                           
          104┆ result = str(eval(expr))  # noqa: S307
   
   ❯❯❱ python.fastapi.os.tainted-os-command-stdlib-fastapi-secure-default.tainted-os-command-stdlib-fastapi-secure-
       default                                                                                                     
          Untrusted input might be injected into a command executed by the application, which can lead to a   
          command injection vulnerability. An attacker can execute arbitrary commands, potentially gaining    
          complete control of the system. To prevent this vulnerability, avoid executing OS commands with user
          input. If this is unavoidable, validate and sanitize the input, and use safe methods for executing  
          the commands. Untrusted input in a command can lead to command injection, allowing attackers to     
          execute arbitrary commands and gain control of the system. To prevent this:                         
                                                                                                              
          1. Avoid direct command execution: Don't run OS commands with user input directly. 2. Validate and  
          sanitize input: Ensure input is safe by removing or escaping dangerous characters. 3. (preferred)   
          Use safe methods: Use `subprocess.run` without `shell=True` to safely execute commands, as it       
          doesn't call a system shell by default. If `shell=True` is necessary, properly quote and escape all 
          input to prevent shell injection. This is a secure by default approach.                             
          Details: https://sg.run/9AzEz                                                                       
                                                                                                              
          112┆ completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # noqa:
               S602,S603                                                                           
    
    
          Taint comes from:
    
          109┆ def debug_run(cmd: str) -> dict[str, str]:
    
    
          Taint flows through these intermediate variables:
    
          109┆ def debug_run(cmd: str) -> dict[str, str]:
    
    
                This is how taint reaches the sink:
    
          112┆ completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # noqa:
               S602,S603                                                                           
    
    
            ⋮┆----------------------------------------
   
   ❯❯❱ python.lang.security.audit.subprocess-shell-true.subprocess-shell-true
          Found 'subprocess' function 'run' with 'shell=True'. This is dangerous because this call will spawn
          the command using a shell process. Doing so propagates current shell settings and variables, which 
          makes it much easier for a malicious actor to execute commands. Use 'shell=False' instead.         
          Details: https://sg.run/J92w                                                                       
                                                                                                             
           ▶▶┆ Autofix ▶ False
          112┆ completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # noqa:
               S602,S603                                                                           
   
    ❯❱ python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
          Detected a dynamic value being used with urllib. urllib supports 'file://' schemes, so a dynamic    
          value controlled by a malicious actor may allow them to read arbitrary files. Audit uses of urllib  
          calls to ensure user data cannot control the URLs, or consider using the 'requests' library instead.
          Details: https://sg.run/dKZZ                                                                        
                                                                                                              
          120┆ with urlopen(url) as res:  # noqa: S310
   
   ❯❯❱ python.fastapi.file.tainted-path-traversal-stdlib-fastapi.tainted-path-traversal-stdlib-fastapi
          The application builds a file path from potentially untrusted data, which can lead to a path        
          traversal vulnerability. An attacker can manipulate the path which the application uses to access   
          files. If the application does not validate user input and sanitize file paths, sensitive files such
          as configuration or user data can be accessed, potentially creating or overwriting files. In FastAPI
          apps, consider using the Starlette `:path` annotation in the route declaration to automatically     
          sanitize paths and filenames.                                                                       
          Details: https://sg.run/WA92Z                                                                       
                                                                                                              
          128┆ content = open(path, "r").read(1024)
    
    
          Taint comes from:
    
          126┆ def debug_read(path: str) -> dict[str, str]:
    
    
          Taint flows through these intermediate variables:
    
          126┆ def debug_read(path: str) -> dict[str, str]:
    
    
                This is how taint reaches the sink:
    
          128┆ content = open(path, "r").read(1024)
    

                
                
┌──────────────┐
│ Scan Summary │
└──────────────┘
✅ CI scan completed successfully.
 • Findings: 38 (0 blocking)
 • Rules run: 121360
 • Targets scanned: 19
 • Parsed lines: ~100.0%
 • Scan skipped: 
   ◦ Files matching .semgrepignore patterns: 5
 • Scan was limited to files tracked by git
 • For a detailed list of skipped files and lines, run semgrep with the --verbose flag
CI scan completed successfully.
  View results in Semgrep Cloud Platform:
    https://semgrep.dev/orgs/khanh-nguyen27122005-hcmut-edu-vn/findings?repo=local_scan/modern-software-dev-assignments/week6&ref=week6/khanh
    https://semgrep.dev/orgs/khanh-nguyen27122005-hcmut-edu-vn/supply-chain/vulnerabilities?repo=local_scan/modern-software-dev-assignments/week6&ref=week6/khanh
  No blocking findings so exiting with code 0
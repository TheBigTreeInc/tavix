workspace "TaviX" "TaviX reviewed extension distribution and local operator management suite, source 0.1.47 (source-labelled blueprint library, operator-local profile import, explicit read-only HTTPS destination probes, guided blueprint review, source game-first version picker, optional digest-verified pack grid/list, local-only publication destination configuration)." {

    // 0.1.23: Klondike 0.1.2 card-back use remains owned by external Tavi + Tavi Assets.
    model {
        // Version 0.1.24: ZipRunner Operations TaviX consumer is an unpublished
        // data-only sample; the Tavi host relay and permission are external and pending.
        operator = person "Extension maintainer" "Reviews, stages and locally tests TaviX extension packages before choosing whether to publish."

        producer = softwareSystem "Extension producer" "Independent application source/build (e.g. Companion or Atrium); supplies compiled bundles to TaviX." "External"
        tavi = softwareSystem "Tavi" "Messenger application that discovers and installs reviewed TaviX extensions." "External"
        ziprunner = softwareSystem "ZipRunner" "Operator-controlled source import, build, workboard and Git review workflow." "External"
        looprd = softwareSystem "LoopRD asset registry" "External authoritative admin role, pack staging, pricing, publishing, revocation and audit; trusted host transport not implemented by TaviX." "External"
        taviAssets = softwareSystem "Tavi Assets" "External canonical data-only .tavia validation, asset pack engine and consumer SDK." "External"
        pages = softwareSystem "GitHub repository and Pages" "External Git source host and static HTTPS distribution of approved TaviX catalog/assets." "External"

        tavix = softwareSystem "TaviX" "Versioned extension packaging, static repository/catalog tooling, package QA, and a loopback-only development preview." {

            adapter = container "Companion post-build staging adapter" "Optional Node.js command that invokes repository.py stage on a compiled Companion bundle." "Node.js script" {
                stageInvocation = component "Staging invocation" "Checks producer bundle/repository presence and starts the Python staging command; never pushes Git." "Node.js child_process"
            }

            cli = container "Repository and validation toolchain" "CLI commands and reusable Python modules for immutable package staging, index verification and exact-package QA." "Python 3 CLI/library" {
                stage = component "Release staging" "Validates the incoming release; refuses changed same-version bytes; copies staged assets into a versioned directory." "Python; tools/repository.py"
                package = component "TaviX archive codec" "Builds deterministic .tavix archives and verifies package lock paths, sizes, SHA-256 and optional manifest classification and asset dependency requests; not publisher trust." "Python; tools/tavix_package.py"
                uiKitContract = component "Offline TaviX UI kit and contract" "Distributes reviewed SVG icon shapes, system-font CSS and accessibility rules for apps; no host API or font CDN." "ES modules, CSS, JSON; sdk/ui-kit/, contracts/tavix-ui-kit-v1.json"
                uiConformance = component "Optional UI kit conformance checker" "Read-only exact reviewed file check for app directory and validated .tavix archive; never claims native acceptance." "Python; tools/tavix_ui_conformance.py"
                gameCompletionContract = component "Game completion result schema" "Documents server-owned game final result envelopes for future Wallet integration; does not validate live game state or grant client mint rights." "JSON schema and AsciiDoc; contracts/tavix-game-completion-v1.schema.json"
                localFileContract = component "Local file import manifest and SDK wire contract" "Validates optional files.local.import and fileImports request filters and documents host-mediated native picker/read/close/cancel; does not open files or grant access." "Python; tools/tavix_local_file_import.py and contracts/tavix-local-file-import-v1.json"
                registryAdminContract = component "Registry admin manifest request and proposed wire contract" "Validates optional assets.registry.admin/v1 request and documents strict host-mediated method schemas; does not issue host grants or call LoopRD." "Python; tools/tavix_registry_admin.py and contracts/tavix-registry-admin-v1.json"
                assetContract = component "Asset dependency request and grant shape validation" "Validates optional per-pack asset requests and permissions and checks host-issued grant subsets as pure data; never authorizes access or installs content." "Python; tools/tavix_asset_dependencies.py, tools/tavix_asset_grants.py"
                catalog = component "Catalog builder and integrity checker" "Validates all on-disk releases, selects the highest version per application and compares/writes canonical tavi.repository.json bytes." "Python; tools/repository.py"
                preflight = component "Windows catalog preflight" "Reconciles only verified safe catalog drift and leaves unexpected releases/tampering blocked." "Python; tools/ziprunner_catalog_preflight.py"
                packageQa = component "Exact-package QA CLI" "Emits bounded manifest, entrypoint, ZIP integrity and hash evidence without claiming real SDK or multiplayer acceptance." "Python; tools/local-client/qa.py"
            }

            releases = container "Versioned release repository" "Reviewed extension release directories, .tavix archives, integrity metadata and canonical tavi.repository.json catalog in the checkout." "Git-tracked filesystem and static content" {
                tags "Data Store"
            }

            previewServer = container "Local preview HTTP server" "Loopback-only developer server providing extension discovery, archive installation/removal and panel asset delivery." "Python 3; http.server" {
                managerFacade = component "Local operator management facade" "Same-origin and CSRF-gated inventory, canonical TAVIA validation, nonauthoritative price proposals, GitHub read identity and exact-receipt LoopRD CLI delegation. No automatic push." "Python; tools/local_client/manager.py"
                eventJournal = component "Private diagnostic event journal" "Records bounded redacted local-operation events and safe canonical TAVIA failure codes with persistent reference IDs. Not LoopRD audit or authority." "Python; tools/local_client/manager_events.py"
                credentialStore = component "OS-user credential vault adapter" "DPAPI CurrentUser on Windows, secure keyring if available, otherwise memory-only; no credential reaches extensions." "Python; tools/local_client/manager_secrets.py"
                api = component "Local HTTP API" "Handles GET /__local_client/apps, GET /__local_client/installed, POST /__local_client/install and DELETE /__local_client/install/{id}/{version}." "Python; SimpleHTTPRequestHandler"
                discovery = component "Staged release discovery" "Enumerates valid panel entrypoints and normalized game/app metadata in versioned repository manifests; for development preview only." "Python; tools/local-client/server.py"
                installer = component "Local package installation" "Validates uploaded archives and optional classification and asset requests, limits extraction size, installs versioned local assets and removes packages on request." "Python; tools/local_client/local_packages.py"
                assets = component "Preview asset serving" "Serves staged files from the checkout and locally installed files under /__local_packages/ via local HTTP." "Python; SimpleHTTPRequestHandler"
            }

            nativeStudio = container "Native TaviX Studio shell (candidate)" "PatternFly operator review, native local Assets source selection, safe validator diagnostics, designer blueprints and preview ZIP handoffs; no remote publication." "Tauri 2 Rust and React/PatternFly 6" {
                studioLifecycle = component "Managed Studio build and start" "Windows: checks npm dependencies, compiles in a dedicated reusable Cargo target, stages immutable SHA-256-verified versioned executables and launches only a receipt-verified copy, avoiding locks on legacy mutable target/release output; no Python management HTTP server." "Python; tools/studio-desktop/build_windows.py and run_windows.py"
                studioRead = component "Native read-only workspace boundary" "Reads fixed checkout metadata, manifest inventory and sanitized event metadata only, without user paths or credentials." "Rust; tools/studio-desktop/src-tauri/src/lib.rs"
                studioReview = component "Native submission review and feedback" "Uses a native picker; enforces canonical validation, local review decisions, private SHA-bound storage and feedback/preview/approval exports without official publication." "Rust plus fixed Python CLI; tools/studio-desktop/review_cli.py"
                studioPackBrowser = component "Read-only submitted pack catalog and artwork preview" "Returns paginated manifest resources, objects, collections and files from retained exact SHA package; safe image preview only, no package execution." "Rust IPC + fixed Python tools/studio-desktop/studio_pack_catalog.py"
                studioGithubCatalog = component "GitHub asset source catalog sync and draft PR" "Reads pinned TheBigTreeInc/tavi-assets editorial/public indexes, checks source/index parity, validates exact local approved TAVIA and prepares metadata-only draft PR after explicit confirmation; no binary upload or official store publication." "Rust IPC + Python gh API; tools/studio-desktop/studio_github_catalog.py"
                studioPublishTargets = component "Operator publication destinations and read-only reachability" "Stores non-secret GitHub repository/LoopRD HTTPS hostname; explicit bounded no-credential HTTPS probes through the fixed trusted CLI; publisher authorization and mutations remain unavailable." "Rust; tools/studio-desktop/src-tauri/src/studio_publish.rs"
                studioBlueprint = component "Designer asset blueprint library and local import" "Shows bundled and operator-imported provenance; validates and stores bounded data-only local-* JSON profiles through native picker and fixed Python; checks required semantic IDs without granting canonical or publishing authority." "JSON and AsciiDoc; tools/studio-desktop/blueprints"
                studioLayout = component "PatternFly desktop layout" "Compact masthead, notification detail, native-picker-first submission import then optional blueprint/custom modal, searchable source-labelled blueprint library, guided blueprint recheck, responsive paginated package viewer, game-first list with version picker, Asset blueprints, Storefront, Connections, Operations and Events; official publishing disabled." "React; tools/studio-desktop/src/main.tsx"
            }

            previewUi = container "Local preview browser UI" "Development-only panel browser with local archive upload, install/remove controls, iframe preview and basic diagnostics." "HTML and JavaScript in a web browser" {
                eventsUi = component "Operator Events view" "Filters and exports sanitized local operation events; no credentials or untrusted archive bytes." "HTML/JavaScript; tools/local-client/index.html and manager.js"
                operatorUi = component "Management suite controls" "Overview, packages, asset drafts/objects, storefront values, GitHub/LoopRD credentials and reviewed operations; remote writes require independent approval." "HTML/CSS/JavaScript; tools/local-client/manager.js"
                libraryUi = component "Extension library controls" "Lists discovered releases and installed versions with game/app labels and asset requests; selects a preview panel, without trusted Tavi inventory." "JavaScript; tools/local-client/index.html"
                installUi = component "Archive installation controls" "Uploads .tavix bytes and requests local package removal; displays status/errors." "JavaScript; tools/local-client/index.html"
                panelUi = component "Sandboxed preview panel" "Loads the selected panel URL in a sandboxed iframe and exposes limited host-side diagnostics; no production Tavi SDK." "HTML iframe; JavaScript"
            }

            managerStore = container "Operator-local draft and encrypted credential store" "Per-user ~/.tavix-suite outside the Git checkout, nonauthoritative asset/price drafts, settings and DPAPI ciphertext; never published." "Private local filesystem" {
                tags "Data Store"
            }

            studioReviewStore = container "Private Studio submissions and review decisions" "Operator-local immutable package copies and SHA-bound feedback/approval records; never public catalog, Wallet or release authority." "Per-user local filesystem" {
                tags "Data Store"
            }

            localStore = container "Local installed package store" "Unpublished, development-only extracted packages under .tavix-local, versioned by application and release." "Local filesystem" {
                tags "Data Store"
            }
        }

        operator -> cli "Runs staging, integrity and package QA commands" "CLI"
        operator -> gameCompletionContract "Reviews proposed completed-game service result and trusted issuer requirements" "AsciiDoc/JSON schema"
        operator -> nativeStudio "Reads local repository status and event identifiers without requiring a localhost management server" "Native desktop window"
        nativeStudio -> releases "Reads versioned app manifests only" "Read-only local filesystem"
        studioRead -> managerStore "Reads sanitized event IDs and codes only" "Read-only local events.jsonl"
        studioLayout -> studioRead "Reads checkout inventory and safe event IDs" "Tauri IPC"
        studioLayout -> studioReview "Imports and reviews submissions, connects canonical local Assets source, exports safe diagnostic codes and feedback ZIPs" "Tauri IPC"
        studioLayout -> studioPackBrowser "Browses retained pack metadata and requests bounded image previews" "Tauri IPC"
        studioPackBrowser -> studioReviewStore "Reads SHA-bound original submissions without executing code" "Private local files"
        studioLayout -> studioPublishTargets "Saves intended, non-secret publication destinations; no remote operations" "Tauri IPC"
        studioLayout -> studioGithubCatalog "Reads GitHub source/index revision, reviews safe proposed TAVIA source record, prepares explicit draft PR" "Tauri IPC"
        studioGithubCatalog -> pages "Reads pinned source and index, creates reviewed draft PR metadata only" "GitHub HTTPS API through native GitHub CLI"
        studioGithubCatalog -> studioReviewStore "Reads exact approved TAVIA archive and SHA-bound local review only" "Private operator filesystem"

        studioReview -> package "Validates .tavix archives with canonical validator" "Fixed Python CLI"
        studioReview -> taviAssets "Validates .tavia archives through canonical local Assets checkout" "Fixed Python CLI"
        studioReview -> studioBlueprint "Checks declared asset resource completeness" "JSON and AsciiDoc"
        studioReview -> studioReviewStore "Retains unmodified source packages and private reviewer decisions" "Per-user filesystem"
        operator -> previewUi "Chooses .tavix files and previews installed or staged extensions" "Local browser"
        producer -> adapter "Runs optional adapter after compiling a Companion extension" "Node.js process"
        adapter -> cli "Invokes repository.py stage with compiled bundle" "Python subprocess"
        ziprunner -> cli "Runs the configured build and post-update verification commands" "Python subprocess"
        ziprunner -> studioLifecycle "Builds and starts the native Studio when Windows prerequisites pass" "Managed build/start subprocess"
        studioLifecycle -> studioRead "Launches the built Tauri executable; Rust owns read-only IPC" "Windows desktop process"
        ziprunner -> releases "Applies reviewed source overlays and maintains operator-controlled Git workflow" "Source files"
        cli -> releases "Stages immutable releases and maintains the canonical catalog" "Filesystem"
        releases -> pages "Provides approved source/catalog/assets after an explicitly reviewed Git push" "Git/Pages workflow; operator gated"
        tavi -> pages "Fetches published catalog and extension assets" "HTTPS"
        tavi -> looprd "Proposed trusted authenticated registry admin transport; NOT implemented by TaviX" "Host-mediated backend protocol pending approval"
        tavi -> taviAssets "Hosts and authorizes asset engine access; external integration pending" "Trusted runtime adapter"

        stageInvocation -> stage "Starts stage command with the compiled bundle" "Process invocation"
        stage -> package "Validates and packs the extension archive" "Python call"
        package -> uiKitContract "Packages UI kit files only when explicitly included by the producer" "Static extension assets"
        uiConformance -> package "Validates app source directory or archive integrity" "Python calls"
        uiConformance -> uiKitContract "Compares exact bundled CSS/JS with reviewed kit" "SHA-compatible byte check"
        package -> assetContract "Validates asset request/permission metadata" "Python call"
        package -> registryAdminContract "Validates privileged admin permission request only" "Python call"
        package -> localFileContract "Validates optional native file import request filters" "Python call"
        stage -> assetContract "Validates reviewed source manifest requests" "Python call"
        stage -> registryAdminContract "Validates requested admin permission, never authorizes it" "Python call"
        stage -> localFileContract "Validates reviewed file import declarations, never grants file access" "Python call"
        stage -> catalog "Checks existing index and regenerates after safe staging" "Python call"
        stage -> releases "Copies an immutable release directory" "Filesystem"
        package -> releases "Reads .tavix archives during release validation" "Filesystem"
        catalog -> releases "Validates releases and reads/writes tavi.repository.json" "Filesystem"
        preflight -> catalog "Computes expected index and verifies bounded reconciliation" "Python calls"
        packageQa -> releases "Checks staged manifest, entrypoint and archive integrity" "Filesystem"

        operator -> previewUi "Connects scoped operator keys and requests only independently approved registry transitions" "Local browser"
        previewUi -> previewServer "Requests catalog, package lifecycle and panel assets" "Loopback HTTP/JSON and static files"
        previewUi -> api "Calls local JSON and archive lifecycle routes" "Loopback HTTP/JSON"
        previewServer -> releases "Reads staged release manifests and serves preview files" "Filesystem"
        previewServer -> localStore "Reads and manages development-only packages" "Filesystem"
        eventJournal -> managerStore "Persists redacted operator diagnostics outside Git source" "Private JSONL"
        managerFacade -> eventJournal "Records success/error IDs for local operator calls" "Python call"
        eventsUi -> managerFacade "Reads sanitized events and copies/exports local diagnostic JSON" "CSRF gated browser API"
        managerFacade -> taviAssets "Validates .tavia using canonical local source checkout subprocess" "Python subprocess"
        managerFacade -> looprd "Calls approved scoped DAPI via canonical Assets operator CLIs only with separate exact-artifact receipts" "HTTPS, operator gated"
        managerFacade -> pages "Reads GitHub authenticated user/repository metadata; never auto-pushes" "GitHub HTTPS API"
        managerFacade -> managerStore "Persists local drafts and nonsecret endpoint configuration" "Private local filesystem"
        credentialStore -> managerStore "Stores DPAPI-encrypted credentials when on Windows" "DPAPI CurrentUser"
        operatorUi -> managerFacade "Uses local JSON API with same-origin Origin and CSRF" "Loopback HTTP"
        api -> discovery "Requests staged extension inventory" "Python call"
        api -> installer "Requests install, list and removal operations" "Python call"
        api -> assets "Delegates asset serving" "Python handler"
        discovery -> releases "Reads staged panel manifests and entrypoints" "Filesystem"
        installer -> package "Uses shared archive and extracted-file verification" "Python import"
        installer -> localFileContract "Exposes validated file import request metadata in local-only listings" "Python import"
        installer -> cli "Calls Python toolchain package validation module" "Python import"
        installer -> localStore "Writes/removes versioned unpacked package files" "Filesystem"
        assets -> releases "Serves staged extension pages and static assets" "Local HTTP response"
        assets -> localStore "Serves locally installed extension pages and assets" "Local HTTP response"
        libraryUi -> api "Lists staged and installed packages" "GET JSON"
        installUi -> api "Uploads/removes local packages" "POST binary / DELETE"
        panelUi -> assets "Loads selected packaged HTML/CSS/JavaScript" "Sandboxed iframe HTTP"
        installUi -> libraryUi "Refreshes installed package list after changes" "Browser event"
        libraryUi -> panelUi "Selects panel URL for preview" "Browser event"

        localDevelopment = deploymentEnvironment "Local development" {
            workstation = deploymentNode "Developer workstation" "Source checkout with Python and a browser; preview bound to 127.0.0.1." "Windows or Linux" {
                processes = deploymentNode "Local tools and storage" "Processes and source directories on the workstation." "Python, Node.js and filesystem" {
                    containerInstance cli
                    containerInstance adapter
                    containerInstance previewServer
                    containerInstance releases
                    containerInstance localStore
                }
                browser = deploymentNode "Local web browser" "Loads http://127.0.0.1:8765/tools/local-client/index.html" "Browser" {
                    containerInstance previewUi
                }
            }
        }
    }

    views {
        systemContext tavix tavixContext "TaviX boundaries and the systems it communicates with" {
            include *
            autoLayout lr
        }

        container tavix tavixContainers "TaviX executables, browser UI and file stores" {
            include *
            autoLayout lr
        }

        component cli tavixPublisherComponents "Publishing, verification and exact-package QA" {
            include *
            autoLayout lr
        }

        component previewServer tavixPreviewServerComponents "Loopback HTTP server and local package installation" {
            include *
            autoLayout lr
        }

        component previewUi tavixPreviewUiComponents "Browser-side development preview responsibilities" {
            include *
            autoLayout lr
        }

        component adapter tavixAdapterComponents "Producer staging adapter" {
            include *
            autoLayout lr
        }

        dynamic tavix tavixReleaseStage "Review-gated staging and publication boundary" {
            producer -> adapter "Runs the optional post-build adapter"
            adapter -> cli "Invokes repository.py stage"
            cli -> releases "Verifies and stages immutable release assets, then writes the canonical index"
            ziprunner -> releases "Imports/reviews files and gates Git actions independently"
            releases -> pages "Supplies approved files if an operator authorizes a push"
            autoLayout lr
        }

        dynamic previewServer tavixLocalInstall "Local developer package installation (not a production Tavi installation)" {
            operator -> previewUi "Selects a local .tavix archive"
            previewUi -> api "POST /__local_client/install with archive bytes"
            api -> installer "Passes upload to local installer"
            installer -> cli "Validates archive and extracted content using shared library"
            installer -> localStore "Installs immutable versioned files"
            api -> installer "Lists installed package metadata"
            installer -> localStore "Reads local versioned manifests"
            autoLayout lr
        }

        deployment tavix "Local development" tavixLocalDeployment "Verified loopback preview layout; no external cloud topology claimed" {
            include *
            autoLayout lr
        }

        // 0.1.57: Studio stores proposed price/listed/testing drafts in its private native profile.
        // Local catalog planning is not a LoopRD price/listing API or entitlement grant.
        // 0.1.54: Studio native review calls an operator-scoped LoopRD DAPI adapter.
        // Server-issued scoped service tokens, receipt-gated stage/publish and
        // read-only TAVIB inspection are source-level boundaries; this model
        // intentionally asserts no deployed/authenticated registry or user grants.
        styles {
            element "Person" {
                shape Person
                background #084C61
                color #ffffff
            }
            element "Software System" {
                background #237A66
                color #ffffff
            }
            element "Container" {
                background #3C8D74
                color #ffffff
            }
            element "Component" {
                background #65A98B
                color #102D25
            }
            element "Data Store" {
                shape Cylinder
                background #416A8B
                color #ffffff
            }
            element "External" {
                background #727A81
                color #ffffff
            }
        }
    }
}

workspace "TaviX" "TaviX reviewed extension distribution and local development preview, based on source 0.1.7." {

    model {
        operator = person "Extension maintainer" "Reviews, stages and locally tests TaviX extension packages before choosing whether to publish."

        producer = softwareSystem "Extension producer" "Independent application source/build (e.g. Companion or Atrium); supplies compiled bundles to TaviX." "External"
        tavi = softwareSystem "Tavi" "Messenger application that discovers and installs reviewed TaviX extensions." "External"
        ziprunner = softwareSystem "ZipRunner" "Operator-controlled source import, build, workboard and Git review workflow." "External"
        pages = softwareSystem "GitHub repository and Pages" "External Git source host and static HTTPS distribution of approved TaviX catalog/assets." "External"

        tavix = softwareSystem "TaviX" "Versioned extension packaging, static repository/catalog tooling, package QA, and a loopback-only development preview." {

            adapter = container "Companion post-build staging adapter" "Optional Node.js command that invokes repository.py stage on a compiled Companion bundle." "Node.js script" {
                stageInvocation = component "Staging invocation" "Checks producer bundle/repository presence and starts the Python staging command; never pushes Git." "Node.js child_process"
            }

            cli = container "Repository and validation toolchain" "CLI commands and reusable Python modules for immutable package staging, index verification and exact-package QA." "Python 3 CLI/library" {
                stage = component "Release staging" "Validates the incoming release; refuses changed same-version bytes; copies staged assets into a versioned directory." "Python; tools/repository.py"
                package = component "TaviX archive codec" "Builds deterministic .tavix archives and verifies package lock paths, sizes, SHA-256 and optional manifest classification; not publisher trust." "Python; tools/tavix_package.py"
                catalog = component "Catalog builder and integrity checker" "Validates all on-disk releases, selects the highest version per application and compares/writes canonical tavi.repository.json bytes." "Python; tools/repository.py"
                preflight = component "Windows catalog preflight" "Reconciles only verified safe catalog drift and leaves unexpected releases/tampering blocked." "Python; tools/ziprunner_catalog_preflight.py"
                packageQa = component "Exact-package QA CLI" "Emits bounded manifest, entrypoint, ZIP integrity and hash evidence without claiming real SDK or multiplayer acceptance." "Python; tools/local-client/qa.py"
            }

            releases = container "Versioned release repository" "Reviewed extension release directories, .tavix archives, integrity metadata and canonical tavi.repository.json catalog in the checkout." "Git-tracked filesystem and static content" {
                tags "Data Store"
            }

            previewServer = container "Local preview HTTP server" "Loopback-only developer server providing extension discovery, archive installation/removal and panel asset delivery." "Python 3; http.server" {
                api = component "Local HTTP API" "Handles GET /__local_client/apps, GET /__local_client/installed, POST /__local_client/install and DELETE /__local_client/install/{id}/{version}." "Python; SimpleHTTPRequestHandler"
                discovery = component "Staged release discovery" "Enumerates valid panel entrypoints and normalized game/app metadata in versioned repository manifests; for development preview only." "Python; tools/local-client/server.py"
                installer = component "Local package installation" "Validates uploaded archives and optional classification, limits extraction size, installs versioned local assets and removes packages on request." "Python; tools/local_client/local_packages.py"
                assets = component "Preview asset serving" "Serves staged files from the checkout and locally installed files under /__local_packages/ via local HTTP." "Python; SimpleHTTPRequestHandler"
            }

            previewUi = container "Local preview browser UI" "Development-only panel browser with local archive upload, install/remove controls, iframe preview and basic diagnostics." "HTML and JavaScript in a web browser" {
                libraryUi = component "Extension library controls" "Lists discovered releases and installed versions with game/app labels; selects a preview panel, without trusted Tavi inventory." "JavaScript; tools/local-client/index.html"
                installUi = component "Archive installation controls" "Uploads .tavix bytes and requests local package removal; displays status/errors." "JavaScript; tools/local-client/index.html"
                panelUi = component "Sandboxed preview panel" "Loads the selected panel URL in a sandboxed iframe and exposes limited host-side diagnostics; no production Tavi SDK." "HTML iframe; JavaScript"
            }

            localStore = container "Local installed package store" "Unpublished, development-only extracted packages under .tavix-local, versioned by application and release." "Local filesystem" {
                tags "Data Store"
            }
        }

        operator -> cli "Runs staging, integrity and package QA commands" "CLI"
        operator -> previewUi "Chooses .tavix files and previews installed or staged extensions" "Local browser"
        producer -> adapter "Runs optional adapter after compiling a Companion extension" "Node.js process"
        adapter -> cli "Invokes repository.py stage with compiled bundle" "Python subprocess"
        ziprunner -> cli "Runs the configured build and post-update verification commands" "Python subprocess"
        ziprunner -> releases "Applies reviewed source overlays and maintains operator-controlled Git workflow" "Source files"
        cli -> releases "Stages immutable releases and maintains the canonical catalog" "Filesystem"
        releases -> pages "Provides approved source/catalog/assets after an explicitly reviewed Git push" "Git/Pages workflow; operator gated"
        tavi -> pages "Fetches published catalog and extension assets" "HTTPS"

        stageInvocation -> stage "Starts stage command with the compiled bundle" "Process invocation"
        stage -> package "Validates and packs the extension archive" "Python call"
        stage -> catalog "Checks existing index and regenerates after safe staging" "Python call"
        stage -> releases "Copies an immutable release directory" "Filesystem"
        package -> releases "Reads .tavix archives during release validation" "Filesystem"
        catalog -> releases "Validates releases and reads/writes tavi.repository.json" "Filesystem"
        preflight -> catalog "Computes expected index and verifies bounded reconciliation" "Python calls"
        packageQa -> releases "Checks staged manifest, entrypoint and archive integrity" "Filesystem"

        previewUi -> previewServer "Requests catalog, package lifecycle and panel assets" "Loopback HTTP/JSON and static files"
        previewUi -> api "Calls local JSON and archive lifecycle routes" "Loopback HTTP/JSON"
        previewServer -> releases "Reads staged release manifests and serves preview files" "Filesystem"
        previewServer -> localStore "Reads and manages development-only packages" "Filesystem"
        api -> discovery "Requests staged extension inventory" "Python call"
        api -> installer "Requests install, list and removal operations" "Python call"
        api -> assets "Delegates asset serving" "Python handler"
        discovery -> releases "Reads staged panel manifests and entrypoints" "Filesystem"
        installer -> package "Uses shared archive and extracted-file verification" "Python import"
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

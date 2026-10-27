#!/usr/bin/env python3
"""Generate the small, dependency-free Xcode project from checked-in sources."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
objects = []

def ident(name):
    return hashlib.sha256(name.encode()).hexdigest()[:24].upper()

def quote(value):
    return json.dumps(value)

def obj(name, body):
    key = ident(name)
    objects.append(f"{key} = {{ {body} }};")
    return key

def ids(items):
    return "(" + ",".join(items) + ",)"

def settings(values):
    return "{" + "".join(f"{key} = {quote(value)};" for key, value in values.items()) + "}"

source_files = sorted(root.glob("App/*.swift")) + sorted(root.glob("Core/Sources/AyahLensCore/*.swift"))
resource_files = sorted((root / "App/Resources").glob("*"))
file_refs, sources, resources = [], [], []
for file in source_files + resource_files:
    path = str(file.relative_to(root))
    kind = "folder" if file.is_dir() else ("sourcecode.swift" if file.suffix == ".swift" else ("text.json" if file.suffix == ".json" else "text"))
    reference = obj(path, f"isa = PBXFileReference; lastKnownFileType = {kind}; path = {quote(path)}; sourceTree = SOURCE_ROOT;")
    file_refs.append(reference)
    build = obj(path + ":build", f"isa = PBXBuildFile; fileRef = {reference};")
    (sources if file.suffix == ".swift" else resources).append(build)

package = obj("meta-package", 'isa = XCRemoteSwiftPackageReference; repositoryURL = "https://github.com/facebook/meta-wearables-dat-ios"; requirement = { kind = exactVersion; version = 1.0.1; };')
products, frameworks = [], []
for name in ["MWDATCore", "MWDATDisplay"]:
    dependency = obj(name, f"isa = XCSwiftPackageProductDependency; package = {package}; productName = {name};")
    products.append(dependency)
    frameworks.append(obj(name + ":build", f"isa = PBXBuildFile; productRef = {dependency};"))
source_phase = obj("sources", f"isa = PBXSourcesBuildPhase; buildActionMask = 2147483647; files = {ids(sources)}; runOnlyForDeploymentPostprocessing = 0;")
resource_phase = obj("resources", f"isa = PBXResourcesBuildPhase; buildActionMask = 2147483647; files = {ids(resources)}; runOnlyForDeploymentPostprocessing = 0;")
framework_phase = obj("frameworks", f"isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = {ids(frameworks)}; runOnlyForDeploymentPostprocessing = 0;")
app_product = obj("app-product", 'isa = PBXFileReference; explicitFileType = wrapper.application; path = AyahLens.app; sourceTree = BUILT_PRODUCTS_DIR;')
product_group = obj("product-group", f"isa = PBXGroup; children = {ids([app_product])}; name = Products; sourceTree = \"<group>\";")
main_group = obj("main-group", f"isa = PBXGroup; children = {ids(file_refs + [product_group])}; sourceTree = \"<group>\";")

target_configs, project_configs = [], []
for config in ["Debug", "Release"]:
    target_values = {
        "PRODUCT_NAME": "AyahLens", "PRODUCT_BUNDLE_IDENTIFIER": "ai.khirad.apps.ayahlens",
        "DEVELOPMENT_TEAM": "65LPT48UNK", "CODE_SIGN_STYLE": "Automatic",
        "INFOPLIST_FILE": "App/Info.plist", "SWIFT_VERSION": "6.0",
        "IPHONEOS_DEPLOYMENT_TARGET": "18.0", "TARGETED_DEVICE_FAMILY": "1",
        "SDKROOT": "iphoneos", "SUPPORTED_PLATFORMS": "iphoneos iphonesimulator",
        "LD_RUNPATH_SEARCH_PATHS": "$(inherited) @executable_path/Frameworks",
        "SWIFT_OPTIMIZATION_LEVEL": "-Onone" if config == "Debug" else "-O",
        "ENABLE_USER_SCRIPT_SANDBOXING": "YES", "MARKETING_VERSION": "0.1.0",
        "CURRENT_PROJECT_VERSION": "1", "GENERATE_INFOPLIST_FILE": "NO"
    }
    target_configs.append(obj("target:" + config, f"isa = XCBuildConfiguration; buildSettings = {settings(target_values)}; name = {config};"))
    project_configs.append(obj("project:" + config, f"isa = XCBuildConfiguration; buildSettings = {{ CLANG_ENABLE_MODULES = YES; }}; name = {config};"))
target_list = obj("target-configs", f"isa = XCConfigurationList; buildConfigurations = {ids(target_configs)}; defaultConfigurationIsVisible = 0; defaultConfigurationName = Release;")
project_list = obj("project-configs", f"isa = XCConfigurationList; buildConfigurations = {ids(project_configs)}; defaultConfigurationIsVisible = 0; defaultConfigurationName = Release;")
target = obj("target", f'isa = PBXNativeTarget; buildConfigurationList = {target_list}; buildPhases = {ids([source_phase, framework_phase, resource_phase])}; buildRules = (); dependencies = (); name = AyahLens; productName = AyahLens; productReference = {app_product}; productType = "com.apple.product-type.application"; packageProductDependencies = {ids(products)};')
project = obj("project", f'isa = PBXProject; attributes = {{ LastUpgradeCheck = 2710; }}; buildConfigurationList = {project_list}; compatibilityVersion = "Xcode 14.0"; developmentRegion = en; knownRegions = (en,Base,); mainGroup = {main_group}; productRefGroup = {product_group}; projectDirPath = ""; projectRoot = ""; targets = {ids([target])}; packageReferences = {ids([package])};')
out = root / "AyahLens.xcodeproj"
out.mkdir(exist_ok=True)
(out / "project.pbxproj").write_text("// !$*UTF8*$!\n{ archiveVersion = 1; classes = {}; objectVersion = 56; objects = {\n" + "\n".join(objects) + f"\n}}; rootObject = {project}; }}\n")
scheme = out / "xcshareddata/xcschemes"
scheme.mkdir(parents=True, exist_ok=True)
(scheme / "AyahLens.xcscheme").write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="2710" version="1.3"><BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries><BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{target}" BuildableName="AyahLens.app" BlueprintName="AyahLens" ReferencedContainer="container:AyahLens.xcodeproj"/></BuildActionEntry></BuildActionEntries></BuildAction><LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB"><BuildableProductRunnable runnableDebuggingMode="0"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{target}" BuildableName="AyahLens.app" BlueprintName="AyahLens" ReferencedContainer="container:AyahLens.xcodeproj"/></BuildableProductRunnable></LaunchAction></Scheme>
''')
print(f"Generated AyahLens.xcodeproj with {len(source_files)} Swift sources.")


properties([
	buildDiscarder(
		logRotator(
			artifactDaysToKeepStr: '', 
			artifactNumToKeepStr: '', 
			daysToKeepStr: '7', 
			numToKeepStr: '15'
		)
	), 
	parameters([
		string(
			defaultValue: 'automation', 
			description: 'Branch where test code was fetched from.', 
			name: 'TEST_BRANCH'
		),
		string(
			defaultValue: 'master', 
			description: 'Branch where installer was built from.', 
			name: 'INSTALLER_BRANCH'
		),
		string(
			defaultValue: '', 
			description: 'Use specific installer name instead of getting latest one by INSTALLERR_BRANCH.', 
			name: 'INSTALLER_NAME'
		),
		string(
			defaultValue: '4.5', 
			description: '', 
			name: 'INSTALLER_VERSION'
		),
		string(
			defaultValue: 'smoke', 
			description: '', 
			name: 'TEST_TYPE'
		),
		string(
			defaultValue: 'Chrome', 
			description: 'Supported value: IE, Chrome, Firefox', 
			name: 'BROWSER_TYPE'
		),
		[
			$class: 'LabelParameterDefinition',
			allNodesMatchingLabel: false,
			defaultValue: 'auto7',
			description: '',
			name: 'label',
			nodeEligibility: [$class: 'AllNodeEligibility'],
			triggerIfResult: 'allCases'
		]
	])
])

timestamps{
	withWorkspace('auto7', 'TCDE'){	
		try{
			env.PROPERTY_APIKEY = '-H "X-JFrog-Art-Api:AKCp2WY1Kb9Xs68829rBntbPZg6oKe4vA4JvXSAp4WDn3FGCaaT4bChMxgpHBzQCUqmomp7yD"'
			
			// Using the 'stage' step without a block argument is deprecated
			stage('CheckOut Source Code'){
				bat "mkdir C:\\Tools\\QSFTSSH > nul || echo bypass error"
				bat "curl ${env.PROPERTY_APIKEY} https://artifactory.labs.quest.com/toad-intelligence-central/Components/QSFT/id_rsa -o C:\\Tools\\QSFTSSH\\id_rsa"
				bat "curl ${env.PROPERTY_APIKEY} https://artifactory.labs.quest.com/toad-intelligence-central/Components/QSFT/id_rsa.pub -o C:\\Tools\\QSFTSSH\\id_rsa.pub"
				bat "curl ${env.PROPERTY_APIKEY} https://artifactory.labs.quest.com/toad-intelligence-central/Components/QSFT/known_hosts -o C:\\Tools\\QSFTSSH\\known_hosts"
			
				bat "xcopy c:\\Tools\\QSFTSSH ${env.USERPROFILE}\\.ssh /I /Y"
				bat "RD /S /Q . > nul || echo bypass error"
				def testRepo = 'TCDE'
				def testBranch = getTestBranch(testRepo, env.TEST_BRANCH)
				checkoutBranch(testRepo, testBranch)
			}
			
			stage('Run Tests'){
				bat "ant -file \"test\\Jenkins Build Scripts\\Automation.xml\" -DINSTALLER_BRANCH=${env.INSTALLER_BRANCH} \"-DINSTALLER_NAME=${env.INSTALLER_NAME}\" -DTEST_BRANCH=${env.TEST_BRANCH} -DINSTALLER_VERSION=${env.INSTALLER_VERSION}  -DTEST_TYPE=${env.TEST_TYPE} -DBROWSER_TYPE=${env.BROWSER_TYPE} -DSiteCode=azure \"-DProductName=TICBundle${env.INSTALLER_VERSION},TICAC4.3\" Preparation"
				
				setBuildName()
				
				bat 'dir'
				
				bat "ant -file \"test\\Jenkins Build Scripts\\Automation.xml\" -DINSTALLER_BRANCH=${env.INSTALLER_BRANCH} \"-DINSTALLER_NAME=${env.INSTALLER_NAME}\" -DTEST_BRANCH=${env.TEST_BRANCH} -DINSTALLER_VERSION=${env.INSTALLER_VERSION}  -DTEST_TYPE=${env.TEST_TYPE} -DBROWSER_TYPE=${env.BROWSER_TYPE} -DSiteCode=azure \"-DProductName=TICBundle${env.INSTALLER_VERSION},TICAC4.3\" RunTestInPython"
				
				bat 'dir'
				
				bat 'type C:\\AutomationLog\\tic_pythontest.log'
			}
			currentBuild.result = "SUCCESS"
		} catch(error){
			currentBuild.result = "FAILURE"
			throw error
		} finally{
			archiveArtifacts allowEmptyArchive: true, artifacts: 'env.txt,test.properties,TestResults/Support_Bundle/*.*'
				
			publishHTML([
						allowMissing: false, 
						alwaysLinkToLastBuild: false, 
						keepAll: true, 
						reportDir: 'TestResults/Support_Bundle/webhtml', 
						reportFiles: 'webtest.html', 
						reportName: 'HTML Report', 
						reportTitles: ''
						])
			
			junit 'TestResults/Support_Bundle/weblog/web_junit_result.xml'
			
			notifySlack()
			
			closeSlaveVM()
		}
	}
}

void withWorkspace(def label, def space, def body){
	node(label){
		ws(space){
			body.call()
		}
	}
}

def getTestBranch(def repo, def branch){
	if (isBranchExist(repo, branch)){
		return branch
	}
	def automationBranch = "automation"
	if (isBranchExist(repo, automationBranch)){
		return automationBranch
	}
}

def isBranchExist(def repo, def branch){
	def cmdStatus = bat(script:"git ls-remote --heads git@github.com:QSFT/${repo}.git ${branch} | findstr ${branch}", returnStatus: true)
	return cmdStatus ==0
}

def checkoutBranch(def repo, def branch){
	echo "Checkout branch: ${branch} from repository: ${repo}"

	bat 'git config --global user.email "intersect.build@quest.com"'
	bat 'git config --global user.name "Intersect Builder"'
	git branch: "${branch}", credentialsId: 'github-tic', url: "git@github.com:QSFT/${repo}.git"
}

def setBuildName(){
	def buildName = readFile 'version.txt'
	currentBuild.displayName = buildName
}

def closeSlaveVM(){
	// add test code branch info
	manager.addShortText("${manager.build.buildVariables.get('TEST_BRANCH')}")

	// delete slave node
	for (slave in hudson.model.Hudson.instance.slaves) {
		manager.listener.logger.println("Found slave node ${slave.name}")
		if (slave.name == manager.envVars["NODE_NAME"]) {
			manager.listener.logger.println("Delete slave node ${slave.name}")
			slave.getComputer().doDoDisconnect("Job finished.")
			slave.getComputer().doDoDelete()
		}
	}
}
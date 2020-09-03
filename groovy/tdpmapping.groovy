this.tdpMapping = [
	"pipeline-testA" : [
		"branchName" : {
			return "tdp_branchA"
		}
	],
]


this.defaultTdpMapping = [
	"branchName" : {
		return 'master'
	},
	"version" : { 
		return '5.2.1'
	}
]


def callMappingOnBranch(trigger, branch){
	return this.callMappingOnBranchWithArgs(trigger, branch, null)
}


def callMappingOnBranchWithArgs(trigger, branch, args){
	triggers = this.tdpMapping.getOrDefault(branch, this.defaultTdpMapping)
	return triggers.getOrDefault(trigger, this.defaultTdpMapping[trigger]).call(args)
}

return this
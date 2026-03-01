# MCP Tool Testing Prompts for Cyclic Peptide Tools

## Tool Discovery Tests

### Prompt 1: List All Tools
"What MCP tools are available for cyclic peptides? Give me a brief description of each."

### Prompt 2: Tool Details
"Explain how to use the calculate_peptide_properties tool, including all parameters."

### Prompt 3: Server Information
"Get information about the CycPep MCP server including available tools and dependencies."

## Sync Tool Tests

### Prompt 4: Property Calculation - Valid SMILES
"Calculate properties for this cyclic peptide SMILES: NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O"

### Prompt 5: Validation - Simple SMILES
"Validate if 'CC(=O)NC1CCCC1C(=O)O' is a valid cyclic peptide"

### Prompt 6: Sequence Conversion
"Convert the peptide sequence 'GRGDSP' to a cyclic peptide SMILES with head-to-tail cyclization"

### Prompt 7: Error Handling
"Calculate properties for an invalid SMILES 'invalid_smiles_string'"

### Prompt 8: Simple Molecule Test
"Validate the SMILES 'C1CCCCC1' as a cyclic peptide (this should fail validation as it's not a peptide)"

## Submit API Tests

### Prompt 9: Submit Membrane Permeability
"Submit a membrane permeability prediction job for the cyclic peptide SMILES: NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O"

### Prompt 10: Submit Structure Prediction
"Submit a 3D structure prediction for cyclo(GRGDSP) with 5 conformers"

### Prompt 11: Submit Batch Analysis
"Submit a batch analysis job using the file 'examples/data/sequences/new_data.csv'"

## Job Management Tests

### Prompt 12: List All Jobs
"List all submitted cyclic peptide computation jobs"

### Prompt 13: Check Job Status
"What's the status of job <job_id>?" (Use actual job ID from previous submissions)

### Prompt 14: Get Job Results
"Show me the results of completed job <job_id>"

### Prompt 15: View Job Logs
"Show the last 30 lines of logs for job <job_id>"

### Prompt 16: Cancel Job
"Cancel the job <job_id>" (Use with running job)

## Batch Processing Tests

### Prompt 17: Multiple SMILES
"Calculate properties for these cyclic peptides:
1. NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O
2. CCCCCOc1ccc(-c2ccc(-c3ccc(C(=O)N[C@H]4C[C@@H](O)[C@@H](O)NC(=O)[C@@H]5[C@@H](O)[C@@H](C)CN5C(=O)[C@H]([C@@H](C)O)NC(=O)[C@H]([C@H](O)[C@@H](O)c5ccc(O)cc5)NC(=O)[C@@H]5C[C@@H](O)CN5C(=O)[C@H]([C@@H](C)O)NC4=O)cc3)cc2)cc1"

### Prompt 18: Batch Results
"Get all results from batch job <batch_job_id>"

## End-to-End Scenarios

### Prompt 19: Full Drug Development Workflow
"For the cyclic peptide sequence GRGDSP:
1. Convert to SMILES with head-to-tail cyclization
2. Validate the resulting structure
3. Calculate molecular properties
4. Submit membrane permeability prediction
Summarize all results and assess drug-likeness."

### Prompt 20: Virtual Library Screening
"I have these cyclic peptide candidates and want to assess their drug potential:
- GRGDSP
- RGDFV
- YIGSR

For each:
1. Convert sequence to SMILES
2. Calculate properties (MW, LogP, TPSA)
3. Identify which ones have MW < 1000 and LogP < 3
4. Rank by drug-likeness"

### Prompt 21: Permeability Comparison
"Submit membrane permeability predictions for these two cyclic peptides and compare:
1. NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O
2. Simple test molecule if needed

Which one is predicted to have better membrane permeability?"

## Utility Tests

### Prompt 22: Cleanup Old Jobs
"Clean up job files older than 1 day to free disk space"

### Prompt 23: System Status
"Check the health and status of the cyclic peptide MCP server including any missing dependencies"

## Error Recovery Tests

### Prompt 24: Invalid File Path
"Calculate properties from the non-existent file '/does/not/exist.csv'"

### Prompt 25: Invalid Job ID
"Get status of job 'invalid_job_id_12345'"

### Prompt 26: Empty Sequence
"Convert an empty peptide sequence '' to SMILES"

### Prompt 27: Malformed Input
"Submit batch analysis with malformed parameters"

## Expected Behaviors

For each test, document:
- Response time (sync tools < 1 min, submit tools return job_id quickly)
- Output format (structured JSON-like responses)
- Error handling (clear, helpful error messages)
- Tool availability (all tools discoverable and callable)
- Job workflow (submit -> status -> result chain works)

## Success Criteria

- [ ] All tools are discoverable via Claude CLI
- [ ] Sync tools execute and return results in < 60 seconds
- [ ] Submit tools return job_id immediately for tracking
- [ ] Job management tools work (list, status, result, log, cancel)
- [ ] Error handling returns structured error messages
- [ ] Invalid inputs are handled gracefully
- [ ] Batch processing works for multiple inputs
- [ ] End-to-end workflows complete successfully
- [ ] File I/O operations work correctly
- [ ] Server info and cleanup utilities function
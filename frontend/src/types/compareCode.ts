// Types
export interface FunctionDiffs {
  strict_comparison: string[];
  unifiedDSL: string;
  structural_error?: string | null;   // renamed
  unified_diff: string;
  diffMetadata: {
    extraInStudent: string[];
    extraInTeacher: string[];
  };
}

export interface ModuleSpecificDiffs {
  function_mismatch: string[];
}

export interface FileDiffs {
  [functionName: string]: FunctionDiffs;
}

export interface Differences {
  module_specific_diffs: ModuleSpecificDiffs;
  function_specific_diffs: {
    [fileName: string]: FileDiffs;
  };
}

export interface CompareCodeResponse {
  message?: string;
  differences?: Differences;
  conclusion?: string;
  error?: string;
  details?: string;
}

// Constants
export const getCurrentYear = () => new Date().getFullYear();

export const YEARS = [
  { value: (getCurrentYear() - 2).toString(), label: (getCurrentYear() - 2).toString() },
  { value: (getCurrentYear() - 1).toString(), label: (getCurrentYear() - 1).toString() },
  { value: getCurrentYear().toString(), label: getCurrentYear().toString() }
];

export const EXERCISES = [
  { value: 'EX01', label: 'EX01' },
  { value: 'EX02', label: 'EX02' },
  { value: 'EX03', label: 'EX03' },
  { value: 'EX04', label: 'EX04' },
  { value: 'EX06', label: 'EX06' },
  { value: 'EX07', label: 'EX07' },
  { value: 'EX08', label: 'EX08' },
  { value: 'EX09', label: 'EX09' }
]; 
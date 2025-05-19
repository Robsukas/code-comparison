/**
 * Code Comparison Types and Constants
 * 
 * This module defines TypeScript interfaces and constants used for code comparison
 * functionality. It includes types for:
 * - Function-level differences
 * - Module-level differences
 * - File-level differences
 * - API response structure
 * 
 * Also includes constants for:
 * - Academic years
 * - Exercise identifiers
 */

/**
 * Represents differences found in a specific function
 * 
 * @interface FunctionDiffs
 * @property {string[]} strict_comparison - List of strict comparison differences
 * @property {string} unifiedDSL - Unified flowchart DSL representation
 * @property {string | null} [structural_error] - Error message from structural comparison
 * @property {string} unified_diff - Unified diff format of the differences
 * @property {Object} diffMetadata - Additional metadata about differences
 * @property {string[]} diffMetadata.extraInStudent - Items present only in student code
 * @property {string[]} diffMetadata.extraInTeacher - Items present only in teacher code
 */
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

/**
 * Represents module-level differences between code
 * 
 * @interface ModuleSpecificDiffs
 * @property {string[]} function_mismatch - List of function mismatches between student and teacher code
 */
export interface ModuleSpecificDiffs {
  function_mismatch: string[];
}

/**
 * Maps function names to their differences
 * 
 * @interface FileDiffs
 * @property {FunctionDiffs} [functionName: string] - Differences for each function in the file
 */
export interface FileDiffs {
  [functionName: string]: FunctionDiffs;
}

/**
 * Complete structure of code differences
 * 
 * @interface Differences
 * @property {ModuleSpecificDiffs} module_specific_diffs - Module-level differences
 * @property {Object} function_specific_diffs - File-level differences
 * @property {FileDiffs} function_specific_diffs[fileName: string] - Differences for each file
 */
export interface Differences {
  module_specific_diffs: ModuleSpecificDiffs;
  function_specific_diffs: {
    [fileName: string]: FileDiffs;
  };
}

/**
 * API response structure for code comparison
 * 
 * @interface CompareCodeResponse
 * @property {string} [message] - Status message
 * @property {Differences} [differences] - Detailed code differences
 * @property {string} [conclusion] - AI-generated analysis conclusion
 * @property {string} [diff_error] - Error from difference generation
 * @property {string} [llm_error] - Error from AI analysis
 * @property {string | null} [llm_model] - Model used for AI analysis
 * @property {string} [error] - General error message
 * @property {string} [details] - Detailed error information
 */
export interface CompareCodeResponse {
  message?: string;
  differences?: Differences;
  conclusion?: string;
  diff_error?: string;
  llm_error?: string;
  llm_model?: string | null;
  error?: string;
  details?: string;
}

/**
 * Gets the current year
 * 
 * @returns {number} Current year as a number
 */
export const getCurrentYear = () => new Date().getFullYear();

/**
 * Available academic years for comparison
 * Includes current year and two previous years
 */
export const YEARS = [
  { value: (getCurrentYear() - 2).toString(), label: (getCurrentYear() - 2).toString() },
  { value: (getCurrentYear() - 1).toString(), label: (getCurrentYear() - 1).toString() },
  { value: getCurrentYear().toString(), label: getCurrentYear().toString() }
];

/**
 * Available exercise identifiers
 * Each exercise has a unique code (EX01-EX09, excluding EX05)
 */
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
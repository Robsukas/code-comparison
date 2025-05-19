"""
GitLab Client Module

This module provides a client for interacting with GitLab's API to fetch code from
student and teacher repositories. It handles authentication, URL construction, and
file content retrieval for code analysis purposes.

The client supports:
- Fetching code from both student and teacher repositories
- Handling different exercise directories and file types
- URL encoding and project ID construction
- Error handling for API requests

Dependencies:
    - requests: For making HTTP requests to GitLab API
    - urllib.parse: For URL encoding

Environment Variables:
    GITLAB_API_URL: Base URL for GitLab API (defaults to https://gitlab.cs.ttu.ee/api/v4)
    GITLAB_PRIVATE_TOKEN: Required authentication token for GitLab API
"""

import os
import requests
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from urllib.parse import quote


class GitLabClient:
    """
    Client for interacting with GitLab's API to fetch code from repositories.
    
    This class handles authentication, URL construction, and file content retrieval
    for both student and teacher repositories. It provides methods for finding
    exercise directories and retrieving code files.
    
    Attributes:
        base_url (str): Base URL for GitLab API
        private_token (str): Authentication token for GitLab API
    """

    def __init__(self):
        """
        Initialize the GitLab client with API configuration.
        
        Raises:
            ValueError: If GITLAB_PRIVATE_TOKEN environment variable is not set
        """
        self.base_url = os.getenv('GITLAB_API_URL', 'https://gitlab.cs.ttu.ee/api/v4')
        self.private_token = os.getenv('GITLAB_PRIVATE_TOKEN')
        if not self.private_token:
            raise ValueError("GITLAB_PRIVATE_TOKEN environment variable is required")

    # Helper methods for URL and project ID building
    def _build_url(self, endpoint: str) -> str:
        """
        Construct a full GitLab API URL from an endpoint.
        
        Args:
            endpoint (str): API endpoint path
            
        Returns:
            str: Complete GitLab API URL
        """
        return f"{self.base_url}/{endpoint}"

    def _get_student_project_id(self, student_id: str, year: str) -> str:
        """
        Construct a student project ID from student ID and year.
        
        Args:
            student_id (str): Student's identifier
            year (str): Academic year
            
        Returns:
            str: Formatted project ID for student repository
        """
        return f"{student_id}/iti0102-{year}"

    def _get_teacher_project_id(self, year: str) -> str:
        """
        Construct a teacher project ID from year.
        
        Args:
            year (str): Academic year
            
        Returns:
            str: Formatted project ID for teacher repository
        """
        return f"iti0102-{year}/ex"

    def _get_encoded_project_id(self, project_id: str) -> str:
        """
        URL encode a project ID for API requests.
        
        Args:
            project_id (str): Project ID to encode
            
        Returns:
            str: URL-encoded project ID
        """
        return quote(project_id, safe='')
    
    def _build_file_path(self, exercise_dir: str, file_name: str) -> str:
        """
        Construct a file path within the exercise directory.
        
        Args:
            exercise_dir (str): Exercise directory name
            file_name (str): Name of the file
            
        Returns:
            str: Complete file path
        """
        return f"EX/{exercise_dir}/{file_name}"

    # API request methods
    def get_file_content(self, project_id: str, file_path: str, ref: str = 'main') -> Optional[str]:
        """
        Fetch file content from GitLab repository.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            file_path: URL-encoded full path to the file
            ref: The name of branch, tag or commit (default: main)
            
        Returns:
            The file content as string if successful, None otherwise
            
        Note:
            Handles URL encoding of both project_id and file_path internally
        """
        encoded_project_id = self._get_encoded_project_id(project_id)
        encoded_file_path = quote(file_path, safe='')
        url = self._build_url(f"projects/{encoded_project_id}/repository/files/{encoded_file_path}/raw")
        params = {'ref': ref}
        headers = {'PRIVATE-TOKEN': self.private_token}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException:
            return None

    def get_exercise_directory(self, exercise: str, student_id: str = None, year: str = None) -> Optional[str]:
        """
        Find the exercise directory that matches the given exercise code.
        
        First tries student repo if student_id is provided, then falls back to teacher repo.
        Performs case-insensitive matching of exercise codes.
        
        Args:
            exercise (str): Exercise code to find (e.g., 'EX02')
            student_id (str, optional): Student's ID to check their repository first
            year (str, optional): Academic year for repository selection
            
        Returns:
            str: Matching exercise directory name if found, None otherwise
            
        Note:
            The search is case-insensitive and matches directory names that start with
            the given exercise code.
        """
        # Try student repo first if student_id is provided
        if student_id:
            student_id = student_id.lower()
            project_id = self._get_student_project_id(student_id, year)
            encoded_project_id = self._get_encoded_project_id(project_id)
            url = self._build_url(f"projects/{encoded_project_id}/repository/tree")
            params = {'path': 'EX', 'ref': 'main'}
            headers = {'PRIVATE-TOKEN': self.private_token}

            try:
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                directories = response.json()
                
                # Convert exercise code to lowercase for matching
                exercise_lower = exercise.lower()
                
                # Find directory that starts with the exercise code
                for dir_info in directories:
                    if dir_info['type'] == 'tree' and dir_info['name'].startswith(exercise_lower):
                        return dir_info['name']
            except requests.exceptions.RequestException:
                pass

        # Fall back to teacher repo
        encoded_teacher_id = self._get_encoded_project_id(self._get_teacher_project_id(year))
        url = self._build_url(f"projects/{encoded_teacher_id}/repository/tree")
        params = {'path': 'EX', 'ref': 'main'}
        headers = {'PRIVATE-TOKEN': self.private_token}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            directories = response.json()
            
            # Convert exercise code to lowercase for matching
            exercise_lower = exercise.lower()
            
            # Find directory that starts with the exercise code
            for dir_info in directories:
                if dir_info['type'] == 'tree' and dir_info['name'].startswith(exercise_lower):
                    return dir_info['name']
            
            return None
        except requests.exceptions.RequestException:
            return None

    # File listing methods
    def get_solution_files(self, exercise_dir: str, year: str) -> List[str]:
        """
        Get all solution files in the exercise directory.
        
        Args:
            exercise_dir (str): The exercise directory name
            year (str): Year of the repository (e.g., '2024')
            
        Returns:
            List[str]: List of solution file names (files ending with '_solution.py')
            
        Note:
            Only returns files that end with '_solution.py'
        """
        encoded_teacher_id = self._get_encoded_project_id(self._get_teacher_project_id(year))
        url = self._build_url(f"projects/{encoded_teacher_id}/repository/tree")
        params = {'path': f'EX/{exercise_dir}', 'ref': 'main'}
        headers = {'PRIVATE-TOKEN': self.private_token}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            files = response.json()
            
            # Filter for solution files
            solution_files = [file_info['name'] for file_info in files 
                            if file_info['type'] == 'blob' and file_info['name'].endswith('_solution.py')]
            return solution_files
        except requests.exceptions.RequestException:
            return []

    def get_student_exercise_files(self, student_id: str, exercise_dir: str, year: str) -> List[str]:
        """
        Get all Python files in the student's exercise directory.
        
        Args:
            student_id (str): Student's ID (e.g., 'ronook')
            exercise_dir (str): The exercise directory name
            year (str): Year of the repository (e.g., '2024')
            
        Returns:
            List[str]: List of Python file names (files ending with '.py')
            
        Note:
            Only returns files that end with '.py'
        """
        # Convert student_id to lowercase
        student_id = student_id.lower()
        project_id = self._get_student_project_id(student_id, year)
        encoded_project_id = self._get_encoded_project_id(project_id)
        
        url = self._build_url(f"projects/{encoded_project_id}/repository/tree")
        params = {'path': f'EX/{exercise_dir}', 'ref': 'main'}
        headers = {'PRIVATE-TOKEN': self.private_token}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            files = response.json()
            
            # Filter for Python files
            python_files = [file_info['name'] for file_info in files 
                          if file_info['type'] == 'blob' and file_info['name'].endswith('.py')]
            return python_files
        except requests.exceptions.RequestException:
            return []

    # Code retrieval methods
    def get_teacher_code(self, exercise: str, year: str) -> Optional[Dict[str, str]]:
        """
        Fetch teacher's code for a specific exercise.
        
        Args:
            exercise (str): Exercise identifier (e.g., 'EX02')
            year (str): Year of the repository (e.g., '2024')
            
        Returns:
            Optional[Dict[str, str]]: Dictionary mapping filenames to their content if successful,
                                    None if exercise directory not found or no solution files exist
                                    
        Note:
            Only retrieves files ending with '_solution.py'
        """
        # Find the exercise directory
        exercise_dir = self.get_exercise_directory(exercise, year=year)
        if not exercise_dir:
            return None
        
        # Get all solution files
        solution_files = self.get_solution_files(exercise_dir, year)
        if not solution_files:
            return None
        
        # Store each file's content separately
        code_dict = {}
        for file_name in solution_files:
            file_path = self._build_file_path(exercise_dir, file_name)
            content = self.get_file_content(self._get_teacher_project_id(year), file_path)
            if content:
                code_dict[file_name] = content
        
        if not code_dict:
            return None
        
        return code_dict

    def get_student_code(self, student_id: str, exercise: str, year: str) -> Optional[Dict[str, str]]:
        """
        Fetch student's code for a specific exercise.
        
        Args:
            student_id (str): Student's ID (e.g., 'ronook')
            exercise (str): Exercise identifier (e.g., 'EX02')
            year (str): Year of the repository (e.g., '2024')
            
        Returns:
            Optional[Dict[str, str]]: Dictionary mapping filenames to their content if successful,
                                    None if exercise directory not found or no Python files exist
                                    
        Note:
            Only retrieves files ending with '.py'
        """
        # Find the exercise directory, trying student repo first
        exercise_dir = self.get_exercise_directory(exercise, student_id, year)
        if not exercise_dir:
            return None
        
        # Get all Python files
        python_files = self.get_student_exercise_files(student_id, exercise_dir, year)
        if not python_files:
            return None

        # Convert student_id to lowercase for project ID
        student_id = student_id.lower()
        project_id = self._get_student_project_id(student_id, year)

        # Store each file's content separately
        code_dict = {}
        for file_name in python_files:
            file_path = self._build_file_path(exercise_dir, file_name)
            content = self.get_file_content(project_id, file_path)
            if content:
                code_dict[file_name] = content
        
        if not code_dict:
            return None
        
        return code_dict 
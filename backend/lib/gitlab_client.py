import os
import requests
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from urllib.parse import quote

class GitLabClient:
    def __init__(self):
        self.base_url = os.getenv('GITLAB_API_URL', 'https://gitlab.cs.ttu.ee/api/v4')
        self.private_token = os.getenv('GITLAB_PRIVATE_TOKEN')
        if not self.private_token:
            raise ValueError("GITLAB_PRIVATE_TOKEN environment variable is required")

    # Helper methods for URL and project ID building
    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint}"

    def _get_student_project_id(self, student_id: str, year: str) -> str:
        return f"{student_id}/iti0102-{year}"

    def _get_teacher_project_id(self, year: str) -> str:
        return f"iti0102-{year}/ex"

    def _get_encoded_project_id(self, project_id: str) -> str:
        return quote(project_id, safe='')
    
    def _build_file_path(self, exercise_dir: str, file_name: str) -> str:
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
            exercise_dir: The exercise directory name
            year: Year of the repository (e.g., '2024')
            
        Returns:
            List of solution file names
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
            student_id: Student's ID (e.g., 'ronook')
            exercise_dir: The exercise directory name
            year: Year of the repository (e.g., '2024')
            
        Returns:
            List of Python file names
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
    def get_teacher_code(self, exercise: str, year: str) -> Optional[str]:
        """
        Fetch teacher's code for a specific exercise.
        
        Args:
            exercise: Exercise identifier (e.g., 'EX02')
            year: Year of the repository (e.g., '2024')
            
        Returns:
            The teacher's code as string if successful, None otherwise
        """
        # Find the exercise directory
        exercise_dir = self.get_exercise_directory(exercise, year=year)
        if not exercise_dir:
            return None
        
        # Get all solution files
        solution_files = self.get_solution_files(exercise_dir, year)
        if not solution_files:
            return None
        
        # Combine all solution files
        combined_code = []
        for file_name in solution_files:
            file_path = self._build_file_path(exercise_dir, file_name)
            content = self.get_file_content(self._get_teacher_project_id(year), file_path)
            if content:
                combined_code.append(content)
        
        if not combined_code:
            return None
        
        return "\n\n".join(combined_code)

    def get_student_code(self, student_id: str, exercise: str, year: str) -> Optional[str]:
        """
        Fetch student's code for a specific exercise.
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

        # Combine all Python files
        combined_code = []
        for file_name in python_files:
            file_path = self._build_file_path(exercise_dir, file_name)
            content = self.get_file_content(project_id, file_path)
            if content:
                combined_code.append(content)
        
        if not combined_code:
            return None
        
        return "\n\n".join(combined_code) 
#!/usr/bin/env python
"""
Route Checker Script

This script checks if all routes in the Flask application are accessible
and responding with appropriate status codes.
"""

import requests
import click
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

# Define base URL
BASE_URL = 'http://localhost:5000'

# Define routes to check
ROUTES = {
    'Public Routes': [
        ('GET', '/'),
        ('GET', '/auth/login'),
        ('GET', '/auth/register'),
        ('GET', '/subjects'),
    ],
    'Protected Routes': [
        ('GET', '/dashboard'),
        ('GET', '/subject/1'),
        ('GET', '/admin/dashboard'),
        ('GET', '/admin/users'),
        ('GET', '/admin/subjects'),
    ],
    'API Routes': [
        ('GET', '/api/subjects'),
        ('GET', '/api/users'),
        ('POST', '/api/subjects'),
        ('GET', '/api/subjects/1'),
    ],
    'Dynamic Routes': [
        ('GET', '/subject/1'),
        ('GET', '/admin/subjects/1/sections'),
        ('GET', '/admin/subjects/1/sections/1/topics'),
        ('GET', '/api/subjects/1/sections/1/topics/1'),
    ]
}

def check_route(method: str, path: str, session=None) -> tuple:
    """Check if a route is accessible."""
    url = f"{BASE_URL}{path}"
    try:
        if session is None:
            session = requests.Session()
        
        if method == 'GET':
            response = session.get(url, allow_redirects=False)
        elif method == 'POST':
            response = session.post(url, json={}, allow_redirects=False)
        
        status = response.status_code
        if status in [200, 201]:
            result = 'OK'
            color = 'green'
        elif status in [301, 302]:
            result = 'Redirect'
            color = 'yellow'
        elif status == 401:
            result = 'Unauthorized'
            color = 'yellow'
        elif status == 404:
            result = 'Not Found'
            color = 'red'
        else:
            result = f'Error ({status})'
            color = 'red'
        
        return status, result, color
    
    except requests.exceptions.ConnectionError:
        return 0, 'Server Not Running', 'red'
    except Exception as e:
        return 0, f'Error: {str(e)}', 'red'

@click.command()
@click.option('--auth', is_flag=True, help='Check with authentication')
@click.option('--port', default=5000, help='Port number the Flask app is running on')
def main(auth, port):
    """Check all routes in the Flask application."""
    global BASE_URL
    BASE_URL = f'http://localhost:{port}'
    
    console.print("\n[bold]Flask Route Checker[/bold]\n")
    
    # Create session for authenticated requests if needed
    session = None
    if auth:
        session = requests.Session()
        # Login to get authentication
        login_data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }
        try:
            response = session.post(f"{BASE_URL}/auth/login", data=login_data)
            if response.status_code != 200:
                console.print("[red]Authentication failed. Proceeding without auth.[/red]\n")
                session = None
        except:
            console.print("[red]Could not authenticate. Proceeding without auth.[/red]\n")
            session = None
    
    # Check each category of routes
    for category, routes in ROUTES.items():
        table = Table(title=f"\n{category}")
        table.add_column("Method", style="cyan")
        table.add_column("Route", style="blue")
        table.add_column("Status", justify="right")
        table.add_column("Result")
        
        for method, path in track(routes, description=f"Checking {category}..."):
            status, result, color = check_route(method, path, session)
            table.add_row(
                method,
                path,
                str(status),
                f"[{color}]{result}[/{color}]"
            )
        
        console.print(table)

if __name__ == '__main__':
    main() 
@echo off
REM NovelMind Neo4j Docker Setup Script
echo ====================================
echo NovelMind Neo4j Installation Script
echo ====================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and wait for it to be ready, then run this script again.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check if Neo4j container already exists
docker ps -a | findstr novelmind-neo4j >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Found existing novelmind-neo4j container
    echo Removing old container...
    docker rm -f novelmind-neo4j >nul 2>&1
    echo [OK] Old container removed
    echo.
)

REM Pull Neo4j image
echo Pulling Neo4j image (this may take a few minutes)...
docker pull neo4j:5.17.0

REM Start Neo4j container
echo.
echo Starting Neo4j container...
docker run -d ^
    --name novelmind-neo4j ^
    -p 7474:7474 ^
    -p 7687:7687 ^
    -e NEO4J_AUTH=neo4j/novelmind2024 ^
    -e NEO4J_ACCEPT_LICENSE_AGREEMENT=yes ^
    -e NEO4J_dbms_memory_heap_max__size=512M ^
    -e NEO4J_dbms_memory_pagecache_size=256M ^
    -v novelmind-neo4j-data:/data ^
    neo4j:5.17.0

if errorlevel 1 (
    echo [ERROR] Failed to start Neo4j container
    pause
    exit /b 1
)

echo.
echo ====================================
echo [SUCCESS] Neo4j is starting!
echo ====================================
echo.
echo Container Name: novelmind-neo4j
echo Web Interface:  http://localhost:7474
echo Bolt Port:      bolt://localhost:7687
echo Username:       neo4j
echo Password:       novelmind2024
echo.
echo Waiting for Neo4j to be ready (this takes ~20-30 seconds)...
timeout /t 25 /nobreak >nul

REM Test connection
echo Testing connection...
docker exec novelmind-neo4j cypher-shell -u neo4j -p novelmind2024 "RETURN 'Connection successful!' as message" >nul 2>&1
if not errorlevel 1 (
    echo [OK] Neo4j is ready!
    echo.
    echo You can now access Neo4j Browser at: http://localhost:7474
    echo Backend is configured to use: bolt://localhost:7687
) else (
    echo [INFO] Neo4j may need a few more seconds to start
    echo Please wait and test manually at: http://localhost:7474
)

echo.
echo ====================================
echo Container Management Commands:
echo ====================================
echo Stop Neo4j:    docker stop novelmind-neo4j
echo Start Neo4j:   docker start novelmind-neo4j
echo Remove Neo4j:  docker rm -f novelmind-neo4j
echo View logs:     docker logs novelmind-neo4j
echo ====================================
echo.
pause

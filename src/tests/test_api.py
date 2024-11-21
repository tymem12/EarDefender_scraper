# import pytest
# import pytest_asyncio
# from fastapi.testclient import TestClient
# from unittest.mock import patch, AsyncMock, MagicMock
# from api.api import app, perform_scraping, scraping_results  # Adjust import paths as needed
# from api.api import InputParams

# client = TestClient(app)

# # Mock input data for tests
# scraping_data = {
#     "analysisId": "test_analysis",
#     "inputParams": {
#         "startingPoint": "https://example.com",
#         "maxDepth": 3,
#         "maxFiles": 10,
#         "maxPages": 5,
#         "model": "sample_model",
#         "maxTimePerFile": 5,
#         "maxTotalTime": 20
#     }
# }

# # Authorization header
# headers = {"Authorization": "Bearer mock_bearer_token"}

# # Fixture to reset scraping_results before each test
# @pytest_asyncio.fixture
# async def reset_scraping_results():
#     scraping_results.clear()

# @pytest.mark.asyncio
# async def test_perform_scraping_success(reset_scraping_results):
#     """Test that perform_scraping completes successfully and updates scraping_results."""
#     analysis_id = "test_analysis"
#     params = InputParams(
#         starting_point="https://example.com",
#         max_depth=3,
#         max_files=10,
#         max_pages=5,
#         model="sample_model",
#         max_time_per_file=5,
#         max_total_time=20
#     )

#     with patch("api.api.WebScraper") as MockWebScraper:
#         mock_scraper = MockWebScraper.return_value
#         mock_scraper.scrape.return_value = ["file1.html", "file2.html"]

#         with patch("aiohttp.ClientSession") as MockClientSession:
#             mock_post = AsyncMock()
#             MockClientSession.return_value.__aenter__.return_value.post = mock_post
#             mock_post.return_value.__aenter__.return_value.status = 200

#             await perform_scraping(analysis_id, params, "mock_bearer_token")

#             # Check scraping_results updated correctly
#             assert scraping_results[analysis_id]["status"] == "completed"
#             mock_scraper.scrape.assert_called_once()

#             # Verify that the report request was sent with correct data
#             mock_post.assert_called_once_with(
#                 "http://host.docker.internal:9090/scraper/report",
#                 json={"analysisId": analysis_id, "newFilePaths": ["file1.html", "file2.html"]},
#                 headers={"Authorization": "Bearer mock_bearer_token"},
#                 timeout=10
#             )


# @pytest.mark.asyncio
# async def test_perform_scraping_failure(reset_scraping_results):
#     """Test that perform_scraping handles a failure and updates scraping_results."""
#     analysis_id = "test_analysis"
#     params = InputParams(
#         starting_point="https://example.com",
#         max_depth=3,
#         max_files=10,
#         max_pages=5,
#         model="sample_model",
#         max_time_per_file=5,
#         max_total_time=20
#     )

#     with patch("api.api.WebScraper") as MockWebScraper:
#         mock_scraper = MockWebScraper.return_value
#         mock_scraper.scrape.side_effect = Exception("Scraping failed")

#         with patch("aiohttp.ClientSession") as MockClientSession:
#             mock_post = AsyncMock()
#             MockClientSession.return_value.__aenter__.return_value.post = mock_post

#             await perform_scraping(analysis_id, params, "mock_bearer_token")

#             assert scraping_results[analysis_id]["status"] == "failed"
#             mock_scraper.scrape.assert_called_once()


# def test_start_scraping(reset_scraping_results):
#     """Test the start_scraping endpoint with a unique analysis_id."""
#     with patch("api.api.WebScraper") as MockWebScraper:
#         mock_scraper = MockWebScraper.return_value
#         mock_scraper.scrape.return_value = ["file1.html", "file2.html"]

#         response = client.post("/scraping/start", json=scraping_data, headers=headers)
#         assert response.status_code == 200
#         assert response.json() == {"analysisId": "test_analysis", "message": "Scraping started"}
#         assert scraping_results["test_analysis"]["status"] == "in_progress"


# def test_start_scraping_duplicate_analysis_id(reset_scraping_results):
#     """Test the start_scraping endpoint when a duplicate analysis_id is used."""
#     # Initialize scraping_results with the same analysis_id
#     scraping_results["test_analysis"] = {"status": "in_progress"}

#     response = client.post("/scraping/start", json=scraping_data, headers=headers)
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Analysis ID already in use"}


# def test_start_scraping_missing_authorization(reset_scraping_results):
#     """Test the start_scraping endpoint with missing authorization header."""
#     response = client.post("/scraping/start", json=scraping_data)
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Authorization header missing"}


# def test_start_scraping_with_invalid_authorization(reset_scraping_results):
#     """Test the start_scraping endpoint with an invalid authorization header format."""
#     invalid_headers = {"Authorization": "InvalidFormat"}
#     response = client.post("/scraping/start", json=scraping_data, headers=invalid_headers)
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Invalid authorization format"}

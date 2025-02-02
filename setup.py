from setuptools import setup, find_packages

setup(
    name="impressionist-ai-services",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.115.7",
        "joblib==1.4.2",
        "openai==1.60.0",
        "pydantic==2.10.6",
        "python-dotenv==1.0.1",
        "supabase==2.11.0",
        "superpowered-sdk==0.1.43",
        "termcolor==2.5.0",
        "uvicorn==0.34.0",
    ],
    python_requires=">=3.8",
)

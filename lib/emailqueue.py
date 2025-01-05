# import os
# import redis
# from rq import Queue, Worker
# from .emailsender import email_sender
# import logging
# from decouple import config

# # Set up logging
# def logging_generate(messagetype, message, filelocation):
#     log_message = f"{messagetype}: {message} (Logged from {filelocation})"
#     logging.basicConfig(level=logging.INFO, filename='email_queue.log', 
#                         format='%(asctime)s - %(levelname)s - %(message)s')
#     logging.info(log_message)

# # Redis connection configuration
# # host = 
# # username =
# # password = 
# # port = config( default=6379)  # Default Redis port

# # Establish a connection to Redis
# redis_conn = redis.StrictRedis(
#     host=config('REDIS_HOST'),
#     port=14582,
#     username= config('REDIS_USERNAME'),
#     password=config('REDIS_PASSWORD'),
#     ssl=True  # Assuming TLS is enabled in your Redis server
# )

# # Create a Queue instance
# email_queue = Queue('emailQueue', connection=redis_conn)

# # Define the email processing function
# def process_email_job(job):
#     """Process email sending job."""
#     print("Email queue hit request")
    
#     # Extract job data
#     to = job['to']
#     subject = job['subject']
#     text = job['text']

#     # Log job processing
#     messagetype = "processing"
#     message = f"Processing job: {job}"
#     filelocation = "emailqueue.py"
#     logging_generate(messagetype, message, filelocation)
    
#     try:
#         # Send the email
#         email_sender(to, subject, text)

#         # Log success
#         messagetype = "success"
#         message = f"Email sent successfully to {to}"
#         filelocation = "emailqueue.py"
#         logging_generate(messagetype, message, filelocation)
        
#         print(f"Email sent successfully to {to}")

#     except Exception as e:
#         # Log error if sending email fails
#         messagetype = "error"
#         message = f"Error sending email to {to}: {str(e)}"
#         filelocation = "emailqueue.py"
#         logging_generate(messagetype, message, filelocation)
        
#         print(f"Error sending email to {to}: {str(e)}")
#         # Mark the job as failed by raising an error
#         raise e

# # Add jobs to the queue
# def add_email_job(to, subject, text):
#     """Add an email job to the queue."""
#     job_data = {'to': to, 'subject': subject, 'text': text}
#     job = email_queue.enqueue(process_email_job, job_data)
    
#     print(f"Job {job.id} added to queue.")
    
# # Event listeners for job completion and failure (handled by RQ's events)
# def job_completed(job, *args):
#     print(f"Email job completed successfully: {job.id}")

# def job_failed(job, *args):
#     print(f"Email job failed: {job.id}, Error: {job.exc_info}")

# # Job completion/failure handlers (you can also listen to these in the worker)
# email_queue.finished_job = job_completed
# email_queue.failed_job = job_failed

# # Starting a worker (usually in a separate process)
# if __name__ == "__main__":
#     worker = Worker([email_queue], connection=redis_conn)
#     worker.work()  # This will start processing jobs
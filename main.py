import uvicorn
import json 

from api import app, process_scheduler

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExportResult, SpanExporter


class JsonSpanExporter(SpanExporter):
  def __init__(self, file_name='spans.json'):
      self.file_name = file_name

  def export(self, spans):
      with open(self.file_name, 'a') as f:
          for span in spans:
              # Convert SpanData to a dictionary and dump it to a JSON format
              span_dict = {
                  "context": {
                      "trace_id": span.context.trace_id,
                      "span_id": span.context.span_id
                  },
                  "name": span.name,
                  "start_time": span.start_time,
                  "end_time": span.end_time,
                  "attributes": dict(span.attributes),
                  "events": [{"name": e.name, "attributes": dict(e.attributes), "time": e.time} for e in span.events],
                  "links": [{"context.trace_id": l.context.trace_id, "context.span_id": l.context.span_id, "attributes": dict(l.attributes)} for l in span.links],
                  "status": {"status_code": span.status.status_code.name, "description": span.status.description},
                  "kind": span.kind.name,
                  "resource": dict(span.resource.attributes)
              }
              f.write(json.dumps(span_dict) + '\n')
      return SpanExportResult.SUCCESS

  def shutdown(self):
      pass


def setup_opentelemetry():
  # Create a tracer provider
  provider = TracerProvider()

  # Create a custom JSON span exporter and attach it to the provider with a batch span processor
  json_exporter = JsonSpanExporter("data/telmetry.json")
  provider.add_span_processor(BatchSpanProcessor(json_exporter))

  # Set the created TracerProvider as the global tracer provider
  trace.set_tracer_provider(provider)

  # Instrument FastAPI to automatically generate spans for incoming requests
  FastAPIInstrumentor.instrument_app(app)

  # Instrument the requests library to automatically generate spans for outgoing HTTP requests
  RequestsInstrumentor().instrument()


if __name__ == '__main__':
  setup_opentelemetry()
  uvicorn.run(app, host="0.0.0.0", port=8000)


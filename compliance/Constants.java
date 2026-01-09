public class Constants {

    public static class Queues {
        public static final String COMPLIANCE = "compliance_queue";
        public static final String LOGISTICS = "logistics_queue";
        public static final String RESULTS = "results_queue";
    }

    public static class Statuses {
        public static final String STARTED = "started";
        public static final String PENDING = "pending";
        public static final String APPROVED = "approved";
        public static final String REJECTED = "rejected";
    }

    public static class RabbitConfig {
        public static final String HOST = System.getenv().getOrDefault("RABBITMQ_HOST", "localhost");
        public static final int PORT = 5672;
    }
}
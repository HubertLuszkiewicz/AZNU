import com.rabbitmq.client.*;
import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeoutException;

public class ComplianceService {

    private static final Gson gson = new Gson();

    public static Channel getChannel() throws IOException, TimeoutException {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost(Constants.RabbitConfig.HOST);
        factory.setPort(Constants.RabbitConfig.PORT);
        Connection connection = factory.newConnection();
        return connection.createChannel();
    }

    public static void main(String[] args) throws IOException, TimeoutException {
        Channel channel = getChannel();
        channel.queueDeclare(Constants.Queues.COMPLIANCE, false, false, false, null);

        System.out.println(" [Compliance] Czekam na wnioski do weryfikacji...");

        DeliverCallback deliverCallback = (consumerTag, delivery) -> {
            String message = new String(delivery.getBody(), StandardCharsets.UTF_8);

            try {
                JsonObject data = gson.fromJson(message, JsonObject.class);
                String reqId = data.get("id").getAsString();
                String wasteType = data.get("waste_type").getAsString();

                System.out.println(" [Compliance] Weryfikacja prawna dla: " + wasteType + " (ID: " + reqId + ")");

                Thread.sleep(10000);

                String status;
                if (wasteType.toLowerCase().contains("radio")) {
                    status = Constants.Statuses.REJECTED;
                    System.out.println(" [Compliance] Decyzja: ODRZUCONO (Nielegalny odpad)");
                } else {
                    status = Constants.Statuses.APPROVED;
                    System.out.println(" [Compliance] Decyzja: ZATWIERDZONO (KPO wygenerowane)");
                }

                JsonObject resultMessage = new JsonObject();
                resultMessage.addProperty("id", reqId);
                resultMessage.addProperty("status", status);

                channel.queueDeclare(Constants.Queues.RESULTS, false, false, false, null);
                channel.basicPublish("", Constants.Queues.RESULTS, null,
                        gson.toJson(resultMessage).getBytes(StandardCharsets.UTF_8));
                System.out.println(" [Compliance] Wynik wysłany do results_queue: " + resultMessage);

            } catch (Exception e) {
                System.err.println("Error processing message: " + e.getMessage());
                e.printStackTrace();
            }
        };

        channel.basicConsume(Constants.Queues.COMPLIANCE, true, deliverCallback, consumerTag -> {
        });
    }
}